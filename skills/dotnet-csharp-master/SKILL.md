---
name: dotnet-csharp-master
description: "Master .NET & C# Enterprise Suite. Modern C# 12, ASP.NET Core, Akka.NET actor systems, REST vs gRPC vs SignalR architecture, and clean patterns."
version: 2.0.0
author: Hermes Agent & Antigravity
metadata:
  hermes:
    tags: [dotnet, csharp, akka, aspnet, backend]
---

# Dotnet Csharp Master



## Sub-Module: akka-net-best-practices

# Akka.NET Best Practices

## When to Use This Skill

Use this skill when:
- Designing actor communication patterns
- Deciding between EventStream and DistributedPubSub
- Implementing error handling in actors
- Understanding supervision strategies
- Choosing between Props patterns and DependencyResolver
- Designing work distribution across nodes
- Creating testable actor systems that can run with or without cluster infrastructure
- Abstracting over Cluster Sharding for local testing scenarios

## Reference Files

- [work-distribution-patterns.md](work-distribution-patterns.md): Database queues, Akka.Streams throttling, outbox pattern
- [cluster-local-abstractions.md](cluster-local-abstractions.md): GenericChildPerEntityParent, IPubSubMediator, execution mode wiring
- [async-cancellation-patterns.md](async-cancellation-patterns.md): Actor-scoped CancellationToken, linked CTS, timeout handling

---

## 1. EventStream vs DistributedPubSub

### Critical: EventStream is LOCAL ONLY

`Context.System.EventStream` is **local to a single ActorSystem process**. It does NOT work across cluster nodes.

```csharp
// BAD: This only works on a single server
// When you add a second server, subscribers on server 2 won't receive events from server 1
Context.System.EventStream.Subscribe(Self, typeof(PostCreated));
Context.System.EventStream.Publish(new PostCreated(postId, authorId));
```

**When EventStream is appropriate:**
- Logging and diagnostics within a single process
- Local event bus for truly single-process applications
- Development/testing scenarios

### Use DistributedPubSub for Multi-Node

For events that must reach actors across multiple cluster nodes, use `Akka.Cluster.Tools.PublishSubscribe`:

```csharp
using Akka.Cluster.Tools.PublishSubscribe;

public class TimelineUpdatePublisher : ReceiveActor
{
    private readonly IActorRef _mediator;

    public TimelineUpdatePublisher()
    {
        // Get the DistributedPubSub mediator
        _mediator = DistributedPubSub.Get(Context.System).Mediator;

        Receive<PublishTimelineUpdate>(msg =>
        {
            // Publish to a topic - reaches all subscribers across all nodes
            _mediator.Tell(new Publish($"timeline:{msg.UserId}", msg.Update));
        });
    }
}
```

### Akka.Hosting Configuration for DistributedPubSub

```csharp
builder.WithDistributedPubSub(role: null); // Available on all roles, or specify a role
```

### Topic Design Patterns

| Pattern | Topic Format | Use Case |
|---------|--------------|----------|
| Per-user | `timeline:{userId}` | Timeline updates, notifications |
| Per-entity | `post:{postId}` | Post engagement updates |
| Broadcast | `system:announcements` | System-wide notifications |
| Role-based | `workers:rss-poller` | Work distribution |

---

## 2. Supervision Strategies

### Key Clarification: Supervision is for CHILDREN

A supervision strategy defined on an actor dictates **how that actor supervises its children**, NOT how the actor itself is supervised.

```csharp
public class ParentActor : ReceiveActor
{
    // This strategy applies to children of ParentActor, NOT to ParentActor itself
    protected override SupervisorStrategy SupervisorStrategy()
    {
        return new OneForOneStrategy(
            maxNrOfRetries: 10,
            withinTimeRange: TimeSpan.FromSeconds(30),
            decider: ex => ex switch
            {
                ArithmeticException => Directive.Resume,
                NullReferenceException => Directive.Restart,
                ArgumentException => Directive.Stop,
                _ => Directive.Escalate
            });
    }
}
```

### Default Supervision Strategy

The default `OneForOneStrategy` already includes rate limiting:
- **10 restarts within 1 second** = actor is permanently stopped
- This prevents infinite restart loops

**You rarely need a custom strategy** unless you have specific requirements.

### When to Define Custom Supervision

**Good reasons:**
- Actor throws exceptions indicating irrecoverable state corruption -> Restart
- Actor throws exceptions that should NOT cause restart (expected failures) -> Resume
- Child failures should affect siblings -> Use `AllForOneStrategy`
- Need different retry limits than the default

**Bad reasons:**
- "Just to be safe" - the default is already safe
- Don't understand what the actor does - understand it first

---

## 3. Error Handling: Supervision vs Try-Catch

### When to Use Try-Catch (Most Cases)

**Use try-catch when:**
- The failure is **expected** (network timeout, invalid input, external service down)
- You know **exactly why** the exception occurred
- You can handle it **gracefully** (retry, return error response, log and continue)
- Restarting would **not help** (same error would occur again)

```csharp
public class RssFeedPollerActor : ReceiveActor
{
    public RssFeedPollerActor()
    {
        ReceiveAsync<PollFeed>(async msg =>
        {
            try
            {
                var feed = await _httpClient.GetStringAsync(msg.FeedUrl);
                var items = ParseFeed(feed);
                // Process items...
            }
            catch (HttpRequestException ex)
            {
                // Expected failure - log and schedule retry
                _log.Warning("Feed {Url} unavailable: {Error}", msg.FeedUrl, ex.Message);
                Context.System.Scheduler.ScheduleTellOnce(
                    TimeSpan.FromMinutes(5), Self, msg, Self);
            }
            catch (XmlException ex)
            {
                // Invalid feed format - log and mark as bad
                _log.Error("Feed {Url} has invalid format: {Error}", msg.FeedUrl, ex.Message);
                Sender.Tell(new FeedPollResult.InvalidFormat(msg.FeedUrl));
            }
        });
    }
}
```

### When to Let Supervision Handle It

**Let exceptions propagate (trigger supervision) when:**
- You have **no idea** why the exception occurred
- The actor's **state might be corrupt**
- A **restart would help** (fresh state, reconnect resources)
- It's a **programming error** (NullReferenceException, InvalidOperationException from bad logic)

### Anti-Pattern: Swallowing Unknown Exceptions

```csharp
// BAD: Swallowing exceptions hides problems
catch (Exception ex)
{
    _log.Error(ex, "Error processing work");
    // Actor continues with potentially corrupt state
}

// GOOD: Handle known exceptions, let unknown ones propagate
catch (HttpRequestException ex)
{
    // Known, expected failure - handle gracefully
    _log.Warning("HTTP request failed: {Error}", ex.Message);
    Sender.Tell(new WorkResult.TransientFailure());
}
// Unknown exceptions propagate to supervision
```

---

## 4. Props vs DependencyResolver

### When to Use Plain Props

**Use `Props.Create()` when:**
- Actor doesn't need `IServiceProvider` or `IRequiredActor<T>`
- All dependencies can be passed via constructor
- Actor is simple and self-contained

```csharp
// Simple actor with no DI needs
public static Props Props(PostId postId, IPostWriteStore store)
    => Akka.Actor.Props.Create(() => new PostEngagementActor(postId, store));
```

### When to Use DependencyResolver

**Use `resolver.Props<T>()` when:**
- Actor needs `IServiceProvider` to create scoped services
- Actor uses `IRequiredActor<T>` to get references to other actors
- Actor has many dependencies that are already in DI container

```csharp
// Registration with DI
builder.WithActors((system, registry, resolver) =>
{
    var actor = system.ActorOf(resolver.Props<OrderProcessorActor>(), "order-processor");
    registry.Register<OrderProcessorActor>(actor);
});
```

### Remote Deployment Considerations

**You almost never need remote deployment.** If you're not doing remote deployment (and you probably aren't):
- `Props.Create(() => new Actor(...))` with closures is fine
- The "serialization issue" warning doesn't apply

For most applications, use **cluster sharding** instead of remote deployment - it handles distribution automatically.

---

## 5. Work Distribution Patterns

When you have many background jobs (RSS feeds, email sending, etc.), don't process them all at once - this causes thundering herd problems.

**Three patterns to solve this:**
1. **Database-Driven Work Queue** - Use `FOR UPDATE SKIP LOCKED` for natural cross-node distribution
2. **Akka.Streams Rate Limiting** - Throttle processing within a single node
3. **Durable Queue (Outbox Pattern)** - Database-backed outbox for reliable processing

See [work-distribution-patterns.md](work-distribution-patterns.md) for full code samples.

---

## 6. Common Mistakes Summary

| Mistake | Why It's Wrong | Fix |
|---------|----------------|-----|
| Using EventStream for cross-node pub/sub | EventStream is local only | Use DistributedPubSub |
| Defining supervision to "protect" an actor | Supervision protects children | Understand the hierarchy |
| Catching all exceptions | Hides bugs, corrupts state | Only catch expected errors |
| Always using DependencyResolver | Adds unnecessary complexity | Use plain Props when possible |
| Processing all background jobs at once | Thundering herd, resource exhaustion | Use database queue + rate limiting |
| Throwing exceptions for expected failures | Triggers unnecessary restarts | Return result types, use messaging |

---

## 7. Quick Reference

### Communication Pattern Decision Tree

```
Need to communicate between actors?
├── Same process only? -> EventStream is fine
├── Across cluster nodes?
│   ├── Point-to-point? -> Use ActorSelection or known IActorRef
│   └── Pub/sub? -> Use DistributedPubSub
└── Fire-and-forget to external system? -> Consider outbox pattern
```

### Error Handling Decision Tree

```
Exception occurred in actor?
├── Expected failure (HTTP timeout, invalid input)?
│   └── Try-catch, handle gracefully, continue
├── State might be corrupt?
│   └── Let supervision restart
├── Unknown cause?
│   └── Let supervision restart
└── Programming error (null ref, bad logic)?
    └── Let supervision restart, fix the bug
```

### Props Decision Tree

```
Creating actor Props?
├── Actor needs IServiceProvider?
│   └── Use resolver.Props<T>()
├── Actor needs IRequiredActor<T>?
│   └── Use resolver.Props<T>()
├── Simple actor with constructor params?
│   └── Use Props.Create(() => new Actor(...))
└── Remote deployment needed?
    └── Probably not - use cluster sharding instead
```

---

## 8. Cluster/Local Mode Abstractions

For applications that need to run both in clustered production and local/test environments, use abstraction patterns to toggle between implementations:

- **`AkkaExecutionMode` enum** - Controls which implementations are used (LocalTest vs Clustered)
- **`GenericChildPerEntityParent`** - Mimics sharding behavior locally using the same `IMessageExtractor`
- **`IPubSubMediator`** - Abstracts DistributedPubSub for swappable local/cluster implementations

See [cluster-local-abstractions.md](cluster-local-abstractions.md) for complete implementation code.

---

## 9. Actor Logging

### Use ILoggingAdapter, Not ILogger<T>

In actors, use `ILoggingAdapter` from `Context.GetLogger()` instead of DI-injected `ILogger<T>`:

```csharp
public class MyActor : ReceiveActor
{
    private readonly ILoggingAdapter _log = Context.GetLogger();

    public MyActor()
    {
        Receive<MyMessage>(msg =>
        {
            _log.Info("Processing message for user {UserId}", msg.UserId);
            _log.Error(ex, "Failed to process {MessageType}", msg.GetType().Name);
        });
    }
}
```

**Why ILoggingAdapter:**
- Integrates with Akka's logging pipeline and supervision
- Supports semantic/structured logging as of v1.5.57
- Method names: `Info()`, `Debug()`, `Warning()`, `Error()` (not `Log*` variants)
- No DI required - obtained directly from actor context

**Don't inject ILogger<T> into actors** - it bypasses Akka's logging infrastructure.

### Semantic Logging (v1.5.57+)

```csharp
// Named placeholders for better log aggregation and querying
_log.Info("Order {OrderId} processed for customer {CustomerId}", order.Id, order.CustomerId);

// Prefer named placeholders over positional
// Good: {OrderId}, {CustomerId}
// Avoid: {0}, {1}
```

---

## 10. Managing Async Operations with CancellationToken

When actors launch async operations via `PipeTo`, those operations can outlive the actor if not properly managed. Key practices:

- **Actor CTS in PostStop** - Always cancel and dispose in `PostStop()`
- **New CTS per operation** - Cancel previous before starting new work
- **Pass token everywhere** - EF Core queries, HTTP calls, etc.
- **Linked CTS for timeouts** - External calls get short timeouts to prevent hanging
- **Graceful handling** - Distinguish timeout vs shutdown in catch blocks

See [async-cancellation-patterns.md](async-cancellation-patterns.md) for complete implementation code.

---

## Sub-Module: csharp-developer

# C# Developer

Senior C# developer with mastery of .NET 8+ and Microsoft ecosystem. Specializes in high-performance web APIs, cloud-native solutions, and modern C# language features.

## When to Use This Skill

- Building ASP.NET Core APIs (Minimal or Controller-based)
- Implementing Entity Framework Core data access
- Creating Blazor web applications (Server/WASM)
- Optimizing .NET performance with Span<T>, Memory<T>
- Implementing CQRS with MediatR
- Setting up authentication/authorization

## Core Workflow

1. **Analyze solution** — Review .csproj files, NuGet packages, architecture
2. **Design models** — Create domain models, DTOs, validation
3. **Implement** — Write endpoints, repositories, services with DI
4. **Optimize** — Apply async patterns, caching, performance tuning
5. **Test** — Write xUnit tests with TestServer; verify 80%+ coverage

> **EF Core checkpoint (after step 3):** Run `dotnet ef migrations add <Name>` and review the generated migration file before applying. Confirm no unintended table/column drops. Roll back with `dotnet ef migrations remove` if needed.

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Modern C# | `references/modern-csharp.md` | Records, pattern matching, nullable types |
| ASP.NET Core | `references/aspnet-core.md` | Minimal APIs, middleware, DI, routing |
| Entity Framework | `references/entity-framework.md` | EF Core, migrations, query optimization |
| Blazor | `references/blazor.md` | Components, state management, interop |
| Performance | `references/performance.md` | Span<T>, async, memory optimization, AOT |

## Constraints

### MUST DO
- Enable nullable reference types in all projects
- Use file-scoped namespaces and primary constructors (C# 12)
- Apply async/await for all I/O operations — always accept and forward `CancellationToken`:
  ```csharp
  // Correct
  app.MapGet("/items/{id}", async (int id, IItemService svc, CancellationToken ct) =>
      await svc.GetByIdAsync(id, ct) is { } item ? Results.Ok(item) : Results.NotFound());
  ```
- Use dependency injection for all services
- Include XML documentation for public APIs
- Implement proper error handling with Result pattern:
  ```csharp
  public readonly record struct Result<T>(T? Value, string? Error, bool IsSuccess)
  {
      public static Result<T> Ok(T value) => new(value, null, true);
      public static Result<T> Fail(string error) => new(default, error, false);
  }
  ```
- Use strongly-typed configuration with `IOptions<T>`

### MUST NOT DO
- Use blocking calls (`.Result`, `.Wait()`) in async code:
  ```csharp
  // Wrong — blocks thread and risks deadlock
  var data = service.GetDataAsync().Result;

  // Correct
  var data = await service.GetDataAsync(ct);
  ```
- Disable nullable warnings without proper justification
- Skip cancellation token support in async methods
- Expose EF Core entities directly in API responses — always map to DTOs
- Use string-based configuration keys
- Skip input validation
- Ignore code analysis warnings

## Output Templates

When implementing .NET features, provide:
1. Domain models and DTOs
2. API endpoints (Minimal API or controllers)
3. Repository/service implementations
4. Configuration setup (Program.cs, appsettings.json)
5. Brief explanation of architectural decisions

## Example: Minimal API Endpoint

```csharp
// Program.cs (file-scoped, .NET 8 minimal API)
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddScoped<IProductService, ProductService>();

var app = builder.Build();

app.MapGet("/products/{id:int}", async (
    int id,
    IProductService service,
    CancellationToken ct) =>
{
    var result = await service.GetByIdAsync(id, ct);
    return result.IsSuccess ? Results.Ok(result.Value) : Results.NotFound(result.Error);
})
.WithName("GetProduct")
.Produces<ProductDto>()
.ProducesProblem(404);

app.Run();
```

## Knowledge Reference

C# 12, .NET 8, ASP.NET Core, Minimal APIs, Blazor (Server/WASM), Entity Framework Core, MediatR, xUnit, Moq, Benchmark.NET, SignalR, gRPC, Azure SDK, Polly, FluentValidation, Serilog

[Documentation](https://jeffallan.github.io/claude-skills/skills/language/csharp-developer/)

---

## Sub-Module: dotnet-backend-patterns

# .NET Backend Development Patterns

Master C#/.NET patterns for building production-grade APIs, MCP servers, and enterprise backends with modern best practices (2024/2025).

## When to Use This Skill

- Developing new .NET Web APIs or MCP servers
- Reviewing C# code for quality and performance
- Designing service architectures with dependency injection
- Implementing caching strategies with Redis
- Writing unit and integration tests
- Optimizing database access with EF Core or Dapper
- Configuring applications with IOptions pattern
- Handling errors and implementing resilience patterns

## Core Concepts

### 1. Project Structure (Clean Architecture)

```
src/
├── Domain/                     # Core business logic (no dependencies)
│   ├── Entities/
│   ├── Interfaces/
│   ├── Exceptions/
│   └── ValueObjects/
├── Application/                # Use cases, DTOs, validation
│   ├── Services/
│   ├── DTOs/
│   ├── Validators/
│   └── Interfaces/
├── Infrastructure/             # External implementations
│   ├── Data/                   # EF Core, Dapper repositories
│   ├── Caching/                # Redis, Memory cache
│   ├── External/               # HTTP clients, third-party APIs
│   └── DependencyInjection/    # Service registration
└── Api/                        # Entry point
    ├── Controllers/            # Or MinimalAPI endpoints
    ├── Middleware/
    ├── Filters/
    └── Program.cs
```

### 2. Dependency Injection Patterns

```csharp
// Service registration by lifetime
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddApplicationServices(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        // Scoped: One instance per HTTP request
        services.AddScoped<IProductService, ProductService>();
        services.AddScoped<IOrderService, OrderService>();

        // Singleton: One instance for app lifetime
        services.AddSingleton<ICacheService, RedisCacheService>();
        services.AddSingleton<IConnectionMultiplexer>(_ =>
            ConnectionMultiplexer.Connect(configuration["Redis:Connection"]!));

        // Transient: New instance every time
        services.AddTransient<IValidator<CreateOrderRequest>, CreateOrderValidator>();

        // Options pattern for configuration
        services.Configure<CatalogOptions>(configuration.GetSection("Catalog"));
        services.Configure<RedisOptions>(configuration.GetSection("Redis"));

        // Factory pattern for conditional creation
        services.AddScoped<IPriceCalculator>(sp =>
        {
            var options = sp.GetRequiredService<IOptions<PricingOptions>>().Value;
            return options.UseNewEngine
                ? sp.GetRequiredService<NewPriceCalculator>()
                : sp.GetRequiredService<LegacyPriceCalculator>();
        });

        // Keyed services (.NET 8+)
        services.AddKeyedScoped<IPaymentProcessor, StripeProcessor>("stripe");
        services.AddKeyedScoped<IPaymentProcessor, PayPalProcessor>("paypal");

        return services;
    }
}

// Usage with keyed services
public class CheckoutService
{
    public CheckoutService(
        [FromKeyedServices("stripe")] IPaymentProcessor stripeProcessor)
    {
        _processor = stripeProcessor;
    }
}
```

### 3. Async/Await Patterns

```csharp
// ✅ CORRECT: Async all the way down
public async Task<Product> GetProductAsync(string id, CancellationToken ct = default)
{
    return await _repository.GetByIdAsync(id, ct);
}

// ✅ CORRECT: Parallel execution with WhenAll
public async Task<(Stock, Price)> GetStockAndPriceAsync(
    string productId,
    CancellationToken ct = default)
{
    var stockTask = _stockService.GetAsync(productId, ct);
    var priceTask = _priceService.GetAsync(productId, ct);

    await Task.WhenAll(stockTask, priceTask);

    return (await stockTask, await priceTask);
}

// ✅ CORRECT: ConfigureAwait in libraries
public async Task<T> LibraryMethodAsync<T>(CancellationToken ct = default)
{
    var result = await _httpClient.GetAsync(url, ct).ConfigureAwait(false);
    return await result.Content.ReadFromJsonAsync<T>(ct).ConfigureAwait(false);
}

// ✅ CORRECT: ValueTask for hot paths with caching
public ValueTask<Product?> GetCachedProductAsync(string id)
{
    if (_cache.TryGetValue(id, out Product? product))
        return ValueTask.FromResult(product);

    return new ValueTask<Product?>(GetFromDatabaseAsync(id));
}

// ❌ WRONG: Blocking on async (deadlock risk)
var result = GetProductAsync(id).Result;  // NEVER do this
var result2 = GetProductAsync(id).GetAwaiter().GetResult(); // Also bad

// ❌ WRONG: async void (except event handlers)
public async void ProcessOrder() { }  // Exceptions are lost

// ❌ WRONG: Unnecessary Task.Run for already async code
await Task.Run(async () => await GetDataAsync());  // Wastes thread
```

### 4. Configuration with IOptions

```csharp
// Configuration classes
public class CatalogOptions
{
    public const string SectionName = "Catalog";

    public int DefaultPageSize { get; set; } = 50;
    public int MaxPageSize { get; set; } = 200;
    public TimeSpan CacheDuration { get; set; } = TimeSpan.FromMinutes(15);
    public bool EnableEnrichment { get; set; } = true;
}

public class RedisOptions
{
    public const string SectionName = "Redis";

    public string Connection { get; set; } = "localhost:6379";
    public string KeyPrefix { get; set; } = "mcp:";
    public int Database { get; set; } = 0;
}

// appsettings.json
{
    "Catalog": {
        "DefaultPageSize": 50,
        "MaxPageSize": 200,
        "CacheDuration": "00:15:00",
        "EnableEnrichment": true
    },
    "Redis": {
        "Connection": "localhost:6379",
        "KeyPrefix": "mcp:",
        "Database": 0
    }
}

// Registration
services.Configure<CatalogOptions>(configuration.GetSection(CatalogOptions.SectionName));
services.Configure<RedisOptions>(configuration.GetSection(RedisOptions.SectionName));

// Usage with IOptions (singleton, read once at startup)
public class CatalogService
{
    private readonly CatalogOptions _options;

    public CatalogService(IOptions<CatalogOptions> options)
    {
        _options = options.Value;
    }
}

// Usage with IOptionsSnapshot (scoped, re-reads on each request)
public class DynamicService
{
    private readonly CatalogOptions _options;

    public DynamicService(IOptionsSnapshot<CatalogOptions> options)
    {
        _options = options.Value;  // Fresh value per request
    }
}

// Usage with IOptionsMonitor (singleton, notified on changes)
public class MonitoredService
{
    private CatalogOptions _options;

    public MonitoredService(IOptionsMonitor<CatalogOptions> monitor)
    {
        _options = monitor.CurrentValue;
        monitor.OnChange(newOptions => _options = newOptions);
    }
}
```

### 5. Result Pattern (Avoiding Exceptions for Flow Control)

```csharp
// Generic Result type
public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }
    public string? ErrorCode { get; }

    private Result(bool isSuccess, T? value, string? error, string? errorCode)
    {
        IsSuccess = isSuccess;
        Value = value;
        Error = error;
        ErrorCode = errorCode;
    }

    public static Result<T> Success(T value) => new(true, value, null, null);
    public static Result<T> Failure(string error, string? code = null) => new(false, default, error, code);

    public Result<TNew> Map<TNew>(Func<T, TNew> mapper) =>
        IsSuccess ? Result<TNew>.Success(mapper(Value!)) : Result<TNew>.Failure(Error!, ErrorCode);

    public async Task<Result<TNew>> MapAsync<TNew>(Func<T, Task<TNew>> mapper) =>
        IsSuccess ? Result<TNew>.Success(await mapper(Value!)) : Result<TNew>.Failure(Error!, ErrorCode);
}

// Usage in service
public async Task<Result<Order>> CreateOrderAsync(CreateOrderRequest request, CancellationToken ct)
{
    // Validation
    var validation = await _validator.ValidateAsync(request, ct);
    if (!validation.IsValid)
        return Result<Order>.Failure(
            validation.Errors.First().ErrorMessage,
            "VALIDATION_ERROR");

    // Business rule check
    var stock = await _stockService.CheckAsync(request.ProductId, request.Quantity, ct);
    if (!stock.IsAvailable)
        return Result<Order>.Failure(
            $"Insufficient stock: {stock.Available} available, {request.Quantity} requested",
            "INSUFFICIENT_STOCK");

    // Create order
    var order = await _repository.CreateAsync(request.ToEntity(), ct);

    return Result<Order>.Success(order);
}

// Usage in controller/endpoint
app.MapPost("/orders", async (
    CreateOrderRequest request,
    IOrderService orderService,
    CancellationToken ct) =>
{
    var result = await orderService.CreateOrderAsync(request, ct);

    return result.IsSuccess
        ? Results.Created($"/orders/{result.Value!.Id}", result.Value)
        : Results.BadRequest(new { error = result.Error, code = result.ErrorCode });
});
```

## Data Access Patterns

### Entity Framework Core

```csharp
// DbContext configuration
public class AppDbContext : DbContext
{
    public DbSet<Product> Products => Set<Product>();
    public DbSet<Order> Orders => Set<Order>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // Apply all configurations from assembly
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);

        // Global query filters
        modelBuilder.Entity<Product>().HasQueryFilter(p => !p.IsDeleted);
    }
}

// Entity configuration
public class ProductConfiguration : IEntityTypeConfiguration<Product>
{
    public void Configure(EntityTypeBuilder<Product> builder)
    {
        builder.ToTable("Products");

        builder.HasKey(p => p.Id);
        builder.Property(p => p.Id).HasMaxLength(40);
        builder.Property(p => p.Name).HasMaxLength(200).IsRequired();
        builder.Property(p => p.Price).HasPrecision(18, 2);

        builder.HasIndex(p => p.Sku).IsUnique();
        builder.HasIndex(p => new { p.CategoryId, p.Name });

        builder.HasMany(p => p.OrderItems)
            .WithOne(oi => oi.Product)
            .HasForeignKey(oi => oi.ProductId);
    }
}

// Repository with EF Core
public class ProductRepository : IProductRepository
{
    private readonly AppDbContext _context;

    public async Task<Product?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        return await _context.Products
            .AsNoTracking()
            .FirstOrDefaultAsync(p => p.Id == id, ct);
    }

    public async Task<IReadOnlyList<Product>> SearchAsync(
        ProductSearchCriteria criteria,
        CancellationToken ct = default)
    {
        var query = _context.Products.AsNoTracking();

        if (!string.IsNullOrWhiteSpace(criteria.SearchTerm))
            query = query.Where(p => EF.Functions.Like(p.Name, $"%{criteria.SearchTerm}%"));

        if (criteria.CategoryId.HasValue)
            query = query.Where(p => p.CategoryId == criteria.CategoryId);

        if (criteria.MinPrice.HasValue)
            query = query.Where(p => p.Price >= criteria.MinPrice);

        if (criteria.MaxPrice.HasValue)
            query = query.Where(p => p.Price <= criteria.MaxPrice);

        return await query
            .OrderBy(p => p.Name)
            .Skip((criteria.Page - 1) * criteria.PageSize)
            .Take(criteria.PageSize)
            .ToListAsync(ct);
    }
}
```

### Dapper for Performance

```csharp
public class DapperProductRepository : IProductRepository
{
    private readonly IDbConnection _connection;

    public async Task<Product?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        const string sql = """
            SELECT Id, Name, Sku, Price, CategoryId, Stock, CreatedAt
            FROM Products
            WHERE Id = @Id AND IsDeleted = 0
            """;

        return await _connection.QueryFirstOrDefaultAsync<Product>(
            new CommandDefinition(sql, new { Id = id }, cancellationToken: ct));
    }

    public async Task<IReadOnlyList<Product>> SearchAsync(
        ProductSearchCriteria criteria,
        CancellationToken ct = default)
    {
        var sql = new StringBuilder("""
            SELECT Id, Name, Sku, Price, CategoryId, Stock, CreatedAt
            FROM Products
            WHERE IsDeleted = 0
            """);

        var parameters = new DynamicParameters();

        if (!string.IsNullOrWhiteSpace(criteria.SearchTerm))
        {
            sql.Append(" AND Name LIKE @SearchTerm");
            parameters.Add("SearchTerm", $"%{criteria.SearchTerm}%");
        }

        if (criteria.CategoryId.HasValue)
        {
            sql.Append(" AND CategoryId = @CategoryId");
            parameters.Add("CategoryId", criteria.CategoryId);
        }

        if (criteria.MinPrice.HasValue)
        {
            sql.Append(" AND Price >= @MinPrice");
            parameters.Add("MinPrice", criteria.MinPrice);
        }

        if (criteria.MaxPrice.HasValue)
        {
            sql.Append(" AND Price <= @MaxPrice");
            parameters.Add("MaxPrice", criteria.MaxPrice);
        }

        sql.Append(" ORDER BY Name OFFSET @Offset ROWS FETCH NEXT @PageSize ROWS ONLY");
        parameters.Add("Offset", (criteria.Page - 1) * criteria.PageSize);
        parameters.Add("PageSize", criteria.PageSize);

        var results = await _connection.QueryAsync<Product>(
            new CommandDefinition(sql.ToString(), parameters, cancellationToken: ct));

        return results.ToList();
    }

    // Multi-mapping for related data
    public async Task<Order?> GetOrderWithItemsAsync(int orderId, CancellationToken ct = default)
    {
        const string sql = """
            SELECT o.*, oi.*, p.*
            FROM Orders o
            LEFT JOIN OrderItems oi ON o.Id = oi.OrderId
            LEFT JOIN Products p ON oi.ProductId = p.Id
            WHERE o.Id = @OrderId
            """;

        var orderDictionary = new Dictionary<int, Order>();

        await _connection.QueryAsync<Order, OrderItem, Product, Order>(
            new CommandDefinition(sql, new { OrderId = orderId }, cancellationToken: ct),
            (order, item, product) =>
            {
                if (!orderDictionary.TryGetValue(order.Id, out var existingOrder))
                {
                    existingOrder = order;
                    existingOrder.Items = new List<OrderItem>();
                    orderDictionary.Add(order.Id, existingOrder);
                }

                if (item != null)
                {
                    item.Product = product;
                    existingOrder.Items.Add(item);
                }

                return existingOrder;
            },
            splitOn: "Id,Id");

        return orderDictionary.Values.FirstOrDefault();
    }
}
```

## Caching Patterns

### Multi-Level Cache with Redis

```csharp
public class CachedProductService : IProductService
{
    private readonly IProductRepository _repository;
    private readonly IMemoryCache _memoryCache;
    private readonly IDistributedCache _distributedCache;
    private readonly ILogger<CachedProductService> _logger;

    private static readonly TimeSpan MemoryCacheDuration = TimeSpan.FromMinutes(1);
    private static readonly TimeSpan DistributedCacheDuration = TimeSpan.FromMinutes(15);

    public async Task<Product?> GetByIdAsync(string id, CancellationToken ct = default)
    {
        var cacheKey = $"product:{id}";

        // L1: Memory cache (in-process, fastest)
        if (_memoryCache.TryGetValue(cacheKey, out Product? cached))
        {
            _logger.LogDebug("L1 cache hit for {CacheKey}", cacheKey);
            return cached;
        }

        // L2: Distributed cache (Redis)
        var distributed = await _distributedCache.GetStringAsync(cacheKey, ct);
        if (distributed != null)
        {
            _logger.LogDebug("L2 cache hit for {CacheKey}", cacheKey);
            var product = JsonSerializer.Deserialize<Product>(distributed);

            // Populate L1
            _memoryCache.Set(cacheKey, product, MemoryCacheDuration);
            return product;
        }

        // L3: Database
        _logger.LogDebug("Cache miss for {CacheKey}, fetching from database", cacheKey);
        var fromDb = await _repository.GetByIdAsync(id, ct);

        if (fromDb != null)
        {
            var serialized = JsonSerializer.Serialize(fromDb);

            // Populate both caches
            await _distributedCache.SetStringAsync(
                cacheKey,
                serialized,
                new DistributedCacheEntryOptions
                {
                    AbsoluteExpirationRelativeToNow = DistributedCacheDuration
                },
                ct);

            _memoryCache.Set(cacheKey, fromDb, MemoryCacheDuration);
        }

        return fromDb;
    }

    public async Task InvalidateAsync(string id, CancellationToken ct = default)
    {
        var cacheKey = $"product:{id}";

        _memoryCache.Remove(cacheKey);
        await _distributedCache.RemoveAsync(cacheKey, ct);

        _logger.LogInformation("Invalidated cache for {CacheKey}", cacheKey);
    }
}

// Stale-while-revalidate pattern
public class StaleWhileRevalidateCache<T>
{
    private readonly IDistributedCache _cache;
    private readonly TimeSpan _freshDuration;
    private readonly TimeSpan _staleDuration;

    public async Task<T?> GetOrCreateAsync(
        string key,
        Func<CancellationToken, Task<T>> factory,
        CancellationToken ct = default)
    {
        var cached = await _cache.GetStringAsync(key, ct);

        if (cached != null)
        {
            var entry = JsonSerializer.Deserialize<CacheEntry<T>>(cached)!;

            if (entry.IsStale && !entry.IsExpired)
            {
                // Return stale data immediately, refresh in background
                _ = Task.Run(async () =>
                {
                    var fresh = await factory(CancellationToken.None);
                    await SetAsync(key, fresh, CancellationToken.None);
                });
            }

            if (!entry.IsExpired)
                return entry.Value;
        }

        // Cache miss or expired
        var value = await factory(ct);
        await SetAsync(key, value, ct);
        return value;
    }

    private record CacheEntry<TValue>(TValue Value, DateTime CreatedAt)
    {
        public bool IsStale => DateTime.UtcNow - CreatedAt > _freshDuration;
        public bool IsExpired => DateTime.UtcNow - CreatedAt > _staleDuration;
    }
}
```

## Testing Patterns

### Unit Tests with xUnit and Moq

```csharp
public class OrderServiceTests
{
    private readonly Mock<IOrderRepository> _mockRepository;
    private readonly Mock<IStockService> _mockStockService;
    private readonly Mock<IValidator<CreateOrderRequest>> _mockValidator;
    private readonly OrderService _sut; // System Under Test

    public OrderServiceTests()
    {
        _mockRepository = new Mock<IOrderRepository>();
        _mockStockService = new Mock<IStockService>();
        _mockValidator = new Mock<IValidator<CreateOrderRequest>>();

        // Default: validation passes
        _mockValidator
            .Setup(v => v.ValidateAsync(It.IsAny<CreateOrderRequest>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new ValidationResult());

        _sut = new OrderService(
            _mockRepository.Object,
            _mockStockService.Object,
            _mockValidator.Object);
    }

    [Fact]
    public async Task CreateOrderAsync_WithValidRequest_ReturnsSuccess()
    {
        // Arrange
        var request = new CreateOrderRequest
        {
            ProductId = "PROD-001",
            Quantity = 5,
            CustomerOrderCode = "ORD-2024-001"
        };

        _mockStockService
            .Setup(s => s.CheckAsync("PROD-001", 5, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new StockResult { IsAvailable = true, Available = 10 });

        _mockRepository
            .Setup(r => r.CreateAsync(It.IsAny<Order>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new Order { Id = 1, CustomerOrderCode = "ORD-2024-001" });

        // Act
        var result = await _sut.CreateOrderAsync(request);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.NotNull(result.Value);
        Assert.Equal(1, result.Value.Id);

        _mockRepository.Verify(
            r => r.CreateAsync(It.Is<Order>(o => o.CustomerOrderCode == "ORD-2024-001"),
            It.IsAny<CancellationToken>()),
            Times.Once);
    }

    [Fact]
    public async Task CreateOrderAsync_WithInsufficientStock_ReturnsFailure()
    {
        // Arrange
        var request = new CreateOrderRequest { ProductId = "PROD-001", Quantity = 100 };

        _mockStockService
            .Setup(s => s.CheckAsync(It.IsAny<string>(), It.IsAny<int>(), It.IsAny<CancellationToken>()))
            .ReturnsAsync(new StockResult { IsAvailable = false, Available = 5 });

        // Act
        var result = await _sut.CreateOrderAsync(request);

        // Assert
        Assert.False(result.IsSuccess);
        Assert.Equal("INSUFFICIENT_STOCK", result.ErrorCode);
        Assert.Contains("5 available", result.Error);

        _mockRepository.Verify(
            r => r.CreateAsync(It.IsAny<Order>(), It.IsAny<CancellationToken>()),
            Times.Never);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    [InlineData(-100)]
    public async Task CreateOrderAsync_WithInvalidQuantity_ReturnsValidationError(int quantity)
    {
        // Arrange
        var request = new CreateOrderRequest { ProductId = "PROD-001", Quantity = quantity };

        _mockValidator
            .Setup(v => v.ValidateAsync(request, It.IsAny<CancellationToken>()))
            .ReturnsAsync(new ValidationResult(new[]
            {
                new ValidationFailure("Quantity", "Quantity must be greater than 0")
            }));

        // Act
        var result = await _sut.CreateOrderAsync(request);

        // Assert
        Assert.False(result.IsSuccess);
        Assert.Equal("VALIDATION_ERROR", result.ErrorCode);
    }
}
```

### Integration Tests with WebApplicationFactory

```csharp
public class ProductsApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;

    public ProductsApiTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace real database with in-memory
                services.RemoveAll<DbContextOptions<AppDbContext>>();
                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb"));

                // Replace Redis with memory cache
                services.RemoveAll<IDistributedCache>();
                services.AddDistributedMemoryCache();
            });
        });

        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task GetProduct_WithValidId_ReturnsProduct()
    {
        // Arrange
        using var scope = _factory.Services.CreateScope();
        var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();

        context.Products.Add(new Product
        {
            Id = "TEST-001",
            Name = "Test Product",
            Price = 99.99m
        });
        await context.SaveChangesAsync();

        // Act
        var response = await _client.GetAsync("/api/products/TEST-001");

        // Assert
        response.EnsureSuccessStatusCode();
        var product = await response.Content.ReadFromJsonAsync<Product>();
        Assert.Equal("Test Product", product!.Name);
    }

    [Fact]
    public async Task GetProduct_WithInvalidId_Returns404()
    {
        // Act
        var response = await _client.GetAsync("/api/products/NONEXISTENT");

        // Assert
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}
```

## Best Practices

### DO

1. **Use async/await** all the way through the call stack
2. **Inject dependencies** through constructor injection
3. **Use IOptions<T>** for typed configuration
4. **Return Result types** instead of throwing exceptions for business logic
5. **Use CancellationToken** in all async methods
6. **Prefer Dapper** for read-heavy, performance-critical queries
7. **Use EF Core** for complex domain models with change tracking
8. **Cache aggressively** with proper invalidation strategies
9. **Write unit tests** for business logic, integration tests for APIs
10. **Use record types** for DTOs and immutable data

### DON'T

1. **Don't block on async** with `.Result` or `.Wait()`
2. **Don't use async void** except for event handlers
3. **Don't catch generic Exception** without re-throwing or logging
4. **Don't hardcode** configuration values
5. **Don't expose EF entities** directly in APIs (use DTOs)
6. **Don't forget** `AsNoTracking()` for read-only queries
7. **Don't ignore** CancellationToken parameters
8. **Don't create** `new HttpClient()` manually (use IHttpClientFactory)
9. **Don't mix** sync and async code unnecessarily
10. **Don't skip** validation at API boundaries

## Common Pitfalls

- **N+1 Queries**: Use `.Include()` or explicit joins
- **Memory Leaks**: Dispose IDisposable resources, use `using`
- **Deadlocks**: Don't mix sync and async, use ConfigureAwait(false) in libraries
- **Over-fetching**: Select only needed columns, use projections
- **Missing Indexes**: Check query plans, add indexes for common filters
- **Timeout Issues**: Configure appropriate timeouts for HTTP clients
- **Cache Stampede**: Use distributed locks for cache population

---

## Sub-Module: dotnet-best-practices

# .NET/C# Best Practices

Your task is to ensure .NET/C# code in ${selection} meets the best practices specific to this solution/project. This includes:

## Documentation & Structure

- Create comprehensive XML documentation comments for all public classes, interfaces, methods, and properties
- Include parameter descriptions and return value descriptions in XML comments
- Follow the established namespace structure: {Core|Console|App|Service}.{Feature}

## Design Patterns & Architecture

- Use primary constructor syntax for dependency injection (e.g., `public class MyClass(IDependency dependency)`)
- Implement the Command Handler pattern with generic base classes (e.g., `CommandHandler<TOptions>`)
- Use interface segregation with clear naming conventions (prefix interfaces with 'I')
- Follow the Factory pattern for complex object creation.

## Dependency Injection & Services

- Use constructor dependency injection with null checks via ArgumentNullException
- Register services with appropriate lifetimes (Singleton, Scoped, Transient)
- Use Microsoft.Extensions.DependencyInjection patterns
- Implement service interfaces for testability

## Resource Management & Localization

- Use ResourceManager for localized messages and error strings
- Separate LogMessages and ErrorMessages resource files
- Access resources via `_resourceManager.GetString("MessageKey")`

## Async/Await Patterns

- Use async/await for all I/O operations and long-running tasks
- Return Task or Task<T> from async methods
- Use ConfigureAwait(false) where appropriate
- Handle async exceptions properly

## Testing Standards

- Use MSTest framework with FluentAssertions for assertions
- Follow AAA pattern (Arrange, Act, Assert)
- Use Moq for mocking dependencies
- Test both success and failure scenarios
- Include null parameter validation tests

## Configuration & Settings

- Use strongly-typed configuration classes with data annotations
- Implement validation attributes (Required, NotEmptyOrWhitespace)
- Use IConfiguration binding for settings
- Support appsettings.json configuration files

## Semantic Kernel & AI Integration

- Use Microsoft.SemanticKernel for AI operations
- Implement proper kernel configuration and service registration
- Handle AI model settings (ChatCompletion, Embedding, etc.)
- Use structured output patterns for reliable AI responses

## Error Handling & Logging

- Use structured logging with Microsoft.Extensions.Logging
- Include scoped logging with meaningful context
- Throw specific exceptions with descriptive messages
- Use try-catch blocks for expected failure scenarios

## Performance & Security

- Use C# 12+ features and .NET 8 optimizations where applicable
- Implement proper input validation and sanitization
- Use parameterized queries for database operations
- Follow secure coding practices for AI/ML operations

## Code Quality

- Ensure SOLID principles compliance
- Avoid code duplication through base classes and utilities
- Use meaningful names that reflect domain concepts
- Keep methods focused and cohesive
- Implement proper disposal patterns for resources

---

## Sub-Module: dotnet-service-communication

# dotnet-service-communication

Higher-level routing skill for choosing the right service communication protocol. Provides a decision matrix mapping requirements (latency, direction, client type, payload format, browser support) to the five primary .NET communication protocols: gRPC, SignalR, SSE, JSON-RPC 2.0, and REST. Routes to specialized skills for implementation depth.

**Out of scope:** HTTP client factory patterns and resilience pipelines -- see [skill:dotnet-http-client] and [skill:dotnet-resilience]. Native AOT architecture and trimming strategies -- see [skill:dotnet-native-aot] for AOT compilation, [skill:dotnet-aot-architecture] for AOT-first design patterns, and [skill:dotnet-trimming] for trim-safe development.

Cross-references: [skill:dotnet-grpc] for gRPC implementation, [skill:dotnet-realtime-communication] for SignalR/SSE/JSON-RPC details, [skill:dotnet-http-client] for REST/HTTP client patterns. See [skill:dotnet-integration-testing] for testing service communication patterns.

---

## Decision Matrix

Use this matrix to choose the right protocol based on your requirements:

| Requirement | gRPC | SignalR | SSE | JSON-RPC 2.0 | REST |
|-------------|------|---------|-----|--------------|------|
| **Direction** | All four patterns | Full-duplex | Server-to-client | Request-response | Request-response |
| **Wire format** | Protobuf (binary) | JSON or MessagePack | Text (JSON lines) | JSON | JSON/XML |
| **Browser support** | gRPC-Web (proxy needed) | Yes (JS client) | Yes (native EventSource) | Via WebSocket | Yes (fetch/XHR) |
| **Contract** | `.proto` schema | Hub interface | Convention | JSON-RPC spec | OpenAPI/Swagger |
| **Latency** | Lowest | Low | Low | Medium | Medium |
| **Throughput** | Highest | High | Moderate | Moderate | Moderate |
| **Streaming** | All 4 patterns | Server + client streaming | Server push only | No | No (chunked transfer) |
| **Connection** | HTTP/2 persistent | WebSocket (with fallback) | HTTP/1.1+ persistent | Transport-dependent | Per-request |
| **Service-to-service** | Excellent | Good | Limited | Niche | Good |
| **AOT-friendly** | Yes (Protobuf) | Yes | Yes | Yes | Yes (with STJ source gen) |

---

## Decision Flowchart

```
Is this service-to-service (no browser)?
├── Yes → Do you need streaming?
│   ├── Yes → gRPC streaming [skill:dotnet-grpc]
│   └── No → Is it request-response?
│       ├── High throughput / binary → gRPC (unary) [skill:dotnet-grpc]
│       └── Standard CRUD / public API → REST [skill:dotnet-http-client]
└── No (browser client) → Do you need real-time?
    ├── Yes → Do you need bidirectional?
    │   ├── Yes → SignalR [skill:dotnet-realtime-communication]
    │   └── No (server push only) → SSE [skill:dotnet-realtime-communication]
    └── No → REST [skill:dotnet-http-client]

Special cases:
- LSP / tooling protocol → JSON-RPC 2.0 [skill:dotnet-realtime-communication]
- Mixed (browser + service-to-service) → REST for browser, gRPC for internal
```

---

## Protocol Profiles

### gRPC

**Best for:** Service-to-service communication, high-throughput streaming, strongly-typed contracts.

- Schema-first development with `.proto` files
- All four streaming patterns: unary, server streaming, client streaming, bidirectional
- Binary serialization (Protobuf) for smallest payloads and fastest throughput
- Built-in code generation for client and server stubs
- Native load balancing and health check protocol support

**When NOT to use:** Direct browser communication (requires gRPC-Web proxy), simple CRUD APIs consumed by external clients, scenarios where human-readable payloads are required.

See [skill:dotnet-grpc] for full implementation details.

### SignalR

**Best for:** Browser-facing real-time applications, interactive dashboards, chat, collaborative features.

- Automatic transport negotiation (WebSocket → SSE → Long Polling)
- Built-in group management and user targeting
- Hub abstraction with strongly-typed interfaces
- Scales with Redis backplane or Azure SignalR Service
- Supports JSON and MessagePack serialization

**When NOT to use:** Server-to-client-only push (use SSE instead), service-to-service (use gRPC instead), scenarios where the SignalR client library cannot be included.

See [skill:dotnet-realtime-communication] for SignalR patterns and hub implementation.

### Server-Sent Events (SSE)

**Best for:** Simple server-to-client push notifications, live feeds, status updates.

- Built-in to ASP.NET Core in .NET 10 via `TypedResults.ServerSentEvents`
- Browser-native `EventSource` API -- no client library needed
- Automatic reconnection with `Last-Event-ID`
- Works through HTTP/1.1 proxies that block WebSocket upgrade
- Lightest-weight real-time option

**When NOT to use:** Bidirectional communication (use SignalR), high-throughput binary streaming (use gRPC), client-to-server messages needed.

See [skill:dotnet-realtime-communication] for SSE implementation details.

### JSON-RPC 2.0

**Best for:** Tooling protocols (Language Server Protocol), structured RPC over simple transports.

- Transport-agnostic (HTTP, WebSocket, stdio, named pipes)
- Well-defined request/response/notification semantics
- Used by Visual Studio, VS Code, and .NET tooling via StreamJsonRpc
- Lightweight alternative to gRPC when schema management is unwanted

**When NOT to use:** Real-time streaming (use SignalR or gRPC), high-throughput service-to-service (use gRPC), standard web APIs (use REST).

See [skill:dotnet-realtime-communication] for JSON-RPC 2.0 patterns.

### REST (HTTP APIs)

**Best for:** Public APIs, standard CRUD operations, broad client compatibility.

- Universal client support (any HTTP client)
- Human-readable payloads (JSON)
- Rich ecosystem (OpenAPI, Swagger UI, API versioning)
- Stateless request-response model
- ASP.NET Core Minimal APIs or MVC controllers

**When NOT to use:** Real-time push (use SSE or SignalR), high-throughput service-to-service (use gRPC), bidirectional streaming (use SignalR or gRPC).

See [skill:dotnet-http-client] for HTTP client patterns, resilience, and `IHttpClientFactory`.

---

## Common Architecture Patterns

### API Gateway with Mixed Protocols

```
Browser ─── REST/SignalR ──→ API Gateway ──→ gRPC ──→ Internal Services
                                          ──→ gRPC ──→ Order Service
                                          ──→ gRPC ──→ Inventory Service
```

Use REST for public-facing APIs and SignalR for real-time browser features. Internal service-to-service communication uses gRPC for performance. The API gateway translates between protocols.

### Event-Driven with SSE

```
Internal Services ──→ Message Broker ──→ SSE Endpoint ──→ Browser Dashboard
                                     ──→ gRPC Stream  ──→ Monitoring Service
```

Internal events flow through a message broker. Browser dashboards consume via SSE. Other services consume via gRPC streaming for higher throughput.

### Dual-Protocol Services

A single ASP.NET Core host can serve both gRPC and REST:

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddGrpc();
builder.Services.AddControllers();

var app = builder.Build();

// gRPC for internal service-to-service
app.MapGrpcService<OrderGrpcService>();

// REST for external clients
app.MapControllers();

// SSE for real-time browser updates
app.MapGet("/events/orders", (OrderEventService svc, CancellationToken ct) =>
    TypedResults.ServerSentEvents(svc.GetEventsAsync(ct)));
```

---

## Key Principles

- **Use gRPC for service-to-service** -- it provides the best throughput, strongly-typed contracts, and all streaming patterns
- **Use REST for public APIs** -- universal client support, human-readable, extensive tooling ecosystem
- **Use SignalR for browser real-time** -- automatic transport negotiation and built-in group management
- **Use SSE for simple server push** -- lightest option when bidirectional communication is not needed
- **Mix protocols when appropriate** -- a single ASP.NET Core host can serve gRPC, REST, SignalR, and SSE simultaneously
- **Route based on client type** -- browser clients get REST/SignalR/SSE; internal services get gRPC

See [skill:dotnet-native-aot] for AOT compilation pipeline and [skill:dotnet-aot-architecture] for AOT-compatible communication patterns.

---

## Agent Gotchas

1. **Do not default to gRPC for browser-facing APIs** -- browsers cannot speak HTTP/2 trailers natively. Use gRPC-Web with a proxy or choose REST/SignalR/SSE.
2. **Do not use SignalR for service-to-service** -- gRPC provides better performance, code generation, and streaming for backend communication.
3. **Do not add SignalR when SSE suffices** -- if you only need server-to-client push, SSE is simpler, requires no client library, and has automatic reconnection built into browsers.
4. **Do not use REST for high-throughput internal communication** -- JSON text serialization and per-request connections add overhead vs gRPC's binary format and persistent HTTP/2 connections.
5. **Do not forget AOT considerations** -- REST endpoints using System.Text.Json need source-generated contexts for AOT. See [skill:dotnet-serialization] for details.
6. **Do not expose gRPC services to untrusted clients without gRPC-Web** -- raw gRPC requires HTTP/2, which is not universally available in all environments (e.g., some proxies, older browsers).

---

## References

- [Choose between gRPC and REST](https://learn.microsoft.com/en-us/aspnet/core/grpc/comparison?view=aspnetcore-10.0)
- [gRPC for .NET](https://learn.microsoft.com/en-us/aspnet/core/grpc/?view=aspnetcore-10.0)
- [SignalR overview](https://learn.microsoft.com/en-us/aspnet/core/signalr/introduction?view=aspnetcore-10.0)
- [Server-Sent Events in .NET 10](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/server-sent-events?view=aspnetcore-10.0)
- [Minimal APIs](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis?view=aspnetcore-10.0)
- [IHttpClientFactory patterns](https://learn.microsoft.com/en-us/dotnet/core/extensions/httpclient-factory)

---