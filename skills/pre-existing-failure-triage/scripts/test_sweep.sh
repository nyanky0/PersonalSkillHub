#!/usr/bin/env bash
# Sweep test per-file supaya kegagalan bisa diatribusikan ke satu berkas.
#
# Pakai:
#   bash scripts/test_sweep.sh [dir_test] [batas_memori] [file_hasil]
#
# Default: tests/Feature, 512M, scratch/test_sweep_result.txt
#
# Kenapa per-file: suite penuh sering OOM atau membanjiri output sehingga berkas
# pemicu tidak kelihatan. Satu proses per berkas membuat kegagalan bisa dipetakan.
# Adaptasi perintah runner (phpunit) untuk stack lain; sisanya tetap sama.

set -u

TESTS_DIR="${1:-tests/Feature}"
MEM="${2:-512M}"
OUT="${3:-scratch/test_sweep_result.txt}"

mkdir -p "$(dirname "$OUT")"
: > "$OUT"

for f in "$TESTS_DIR"/*.php; do
    [ -e "$f" ] || continue

    res=$(php -d memory_limit="$MEM" vendor/bin/phpunit "$f" 2>&1 | tail -4 | tr -d '\r' | tr '\n' ' ')

    if echo "$res" | grep -q "OK ("; then
        echo "PASS  $f" >> "$OUT"
    elif echo "$res" | grep -qiE "memory size|Failures|Errors"; then
        echo "FAIL  $f  :: $res" >> "$OUT"
    else
        echo "UNKNOWN $f :: $res" >> "$OUT"
    fi
done

echo "SWEEP DONE" >> "$OUT"
echo "Hasil sweep: $OUT"
echo "Ringkasan:"
grep -c '^PASS' "$OUT" 2>/dev/null | sed 's/^/  PASS: /'
grep -c '^FAIL' "$OUT" 2>/dev/null | sed 's/^/  FAIL: /'
grep -c '^UNKNOWN' "$OUT" 2>/dev/null | sed 's/^/  UNKNOWN: /'
