# Native Notification Listener Plugin for Capacitor

Auto-capture bank/e-wallet notifications without manual sharing. Requires a custom Android NotificationListenerService registered as a Capacitor plugin.

## Architecture

```
Android OS (notification posted)
  → GDBNotificationListener (NotificationListenerService, Java)
    → GDBNotifPlugin.getInstance().onNotificationCaptured(text, pkg)
      → plugin.parseNotification(text, pkg) → JSObject
        → notifyListeners("notificationCaptured", data)
          → JS listener (notifListener.js) receives event
            → auto-save to transactions table with source='notification'
```

## Files Required

### 1. GDBNotificationListener.java
Path: `android/app/src/main/java/<package>/GDBNotificationListener.java`

Extends `NotificationListenerService`. Key methods:
- `onNotificationPosted(StatusBarNotification sbn)`: filters by package name (bank/e-wallet apps), extracts text via `Notification.extras`, calls `GDBNotifPlugin.getInstance().onNotificationCaptured(notifText, pkg)`.
- Filtered packages: BCA, BRI, Mandiri, BNI, GoPay, OVO, DANA, ShopeePay, LinkAja, Blu, BRIMO, Livin', OCTO, Jenius, Neo Commerce.
- Text extraction: `extras.getCharSequence("android.title")` + `extras.getCharSequence("android.text")` + `extras.getCharSequence("android.bigText")`. Concatenate all non-null.
- `onListenerConnected()`: sets `GDBNotifPlugin.getInstance().setListenerActive(true)`.
- `onListenerDisconnected()`: sets `GDBNotifPlugin.getInstance().setListenerActive(false)`.

### 2. GDBNotifPlugin.java
Path: `android/app/src/main/java/<package>/GDBNotifPlugin.java`

Extends `com.getcapacitor.Plugin`. Annotated with `@CapacitorPlugin(name = "GDBNotif")`. Uses **singleton pattern**:

```java
public class GDBNotifPlugin extends Plugin {
    private static GDBNotifPlugin instance;
    private boolean listenerActive = false;

    public GDBNotifPlugin() { instance = this; }
    public static GDBNotifPlugin getInstance() { return instance; }
    public void setListenerActive(boolean active) { this.listenerActive = active; }

    // Called by GDBNotificationListener when bank notif captured
    public void onNotificationCaptured(String text, String packageName) {
        JSObject data = parseNotification(text, packageName);
        if (data != null) {
            notifyListeners("notificationCaptured", data);
        }
    }

    @PluginMethod
    public void checkPermission(PluginCall call) {
        ComponentName cn = new ComponentName(getContext(), GDBNotificationListener.class);
        String flat = Settings.Secure.getString(
            getContext().getContentResolver(), "enabled_notification_listeners");
        boolean enabled = flat != null && flat.contains(cn.flattenToString());
        JSObject result = new JSObject();
        result.put("granted", enabled);
        result.put("listenerActive", listenerActive);
        call.resolve(result);
    }

    @PluginMethod
    public void openSettings(PluginCall call) {
        Intent intent = new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS);
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        getContext().startActivity(intent);
        call.resolve();
    }

    @PluginMethod
    public void parseText(PluginCall call) { /* manual parse from JS */ }
}
```

### 3. AndroidManifest.xml additions

Inside `<application>`, add the service:
```xml
<service
    android:name=".GDBNotificationListener"
    android:label="GDB Notifikasi Bank"
    android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE"
    android:exported="true">
    <intent-filter>
        <action android:name="android.service.notification.NotificationListenerService" />
    </intent-filter>
</service>
```

No additional `<uses-permission>` needed — `BIND_NOTIFICATION_LISTENER_SERVICE` is a service-level permission, not a manifest permission.

### 4. MainActivity.java registration

```java
public class MainActivity extends BridgeActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        registerPlugin(GDBNotifPlugin.class);  // BEFORE super.onCreate()
        super.onCreate(savedInstanceState);
    }
}
```

### 5. JS bridge (src/utils/notifListener.js)

```js
import { Capacitor } from '@capacitor/core'
import db from '../db'

let GDBNotif = null
let listening = false

async function getPlugin() {
  if (GDBNotif) return GDBNotif
  if (!Capacitor.isNativePlatform()) return null
  const mod = await import('@capacitor/core')
  GDBNotif = mod.registerPlugin('GDBNotif')
  return GDBNotif
}

export async function checkNotifPermission() {
  const plugin = await getPlugin()
  if (!plugin) return { granted: false, listenerActive: false, isNative: false }
  try {
    return { ...await plugin.checkPermission(), isNative: true }
  } catch (e) {
    return { granted: false, listenerActive: false, isNative: true }
  }
}

export async function openNotifSettings() {
  const plugin = await getPlugin()
  await plugin?.openSettings()
}

export async function startNotifListener() {
  if (listening) return
  const plugin = await getPlugin()
  if (!plugin) return
  plugin.addListener('notificationCaptured', async (data) => {
    if (!data?.parsed) return
    const cat = data.type === 'income'
      ? await db.get("SELECT id FROM categories WHERE type='income' LIMIT 1")
      : await db.get("SELECT id FROM categories WHERE type='expense' AND name='Lainnya' LIMIT 1")
    await db.run(
      'INSERT INTO transactions (type,amount,category_id,note,date,source,user,sumber_dana) VALUES (?,?,?,?,?,?,?,?)',
      [data.type, data.amount, cat?.id || null, data.note || 'Notifikasi bank', data.date, 'notification', 'Maulana', 'rekening']
    )
  })
  listening = true
}
```

### 6. App.vue integration

```js
import { checkNotifPermission, startNotifListener } from './utils/notifListener'

onMounted(async () => {
  await db.init()
  if (Capacitor.isNativePlatform()) {
    const status = await checkNotifPermission()
    if (status.granted) await startNotifListener()
  }
})
```

## User Permission Flow (CRITICAL)

This permission CANNOT be granted programmatically. User must:
1. Open Settings → Apps → Special access → Notification access
2. Find the app in the list
3. Toggle it ON

The plugin's `openSettings()` method launches the correct settings page directly, but the user still must toggle the switch manually. Show a status badge in settings UI:
- Green "Aktif" if `checkPermission()` returns `granted: true`
- Orange "Belum aktif — tap untuk izinkan" if false, with `openNotifSettings()` on tap
- "Refresh" button to re-check status after user returns from settings

## Pitfalls

- **`BIND_NOTIFICATION_LISTENER_SERVICE` is NOT a `<uses-permission>`**. It's declared on the `<service>` element. Adding it as `<uses-permission>` causes install failure.
- **Singleton vs static handle**: The singleton pattern (`instance = this` in constructor, `getInstance()` static method) is simpler than the `handle` field pattern. The service calls `GDBNotifPlugin.getInstance().onNotificationCaptured()`. No need for a separate `startListening()` JS call to store the handle.
- **Notification text may be null**: Some apps use `EXTRA_TEXT` (body), some use `EXTRA_BIG_TEXT` (expanded), some use `EXTRA_TITLE` only. Always check null and concatenate title + text + bigText.
- **Package name filtering**: Only process notifications from known bank/e-wallet packages. Processing ALL notifications would spam the database and drain battery.
- **Grouped notifications**: Android may post summary notifications for grouped notifs. Check `sbn.isGroup()` and skip summaries to avoid duplicates.
- **Web platform**: `registerPlugin('GDBNotif')` will throw if called on web. Always guard with `Capacitor.isNativePlatform()`.
- **Permission survives reinstall**: Once granted, the permission persists across app updates but NOT across uninstalls.
- **`BridgeActivity.onResume()` is `final`**: You cannot override it. Use `onNewIntent()` for intent handling.
