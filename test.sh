#!/usr/bin/env bash

PASS=0
FAIL=0
SKIP=0

for cantor in tests/*.cantor; do
    base="${cantor%.cantor}"
    name=$(basename "$base")

    if [ ! -f "$base.inp" ] || [ ! -f "$base.out" ]; then
        echo "SKIP $name  (falta .inp o .out)"
        SKIP=$((SKIP + 1))
        continue
    fi

    got=$(python3 cantor.py "$cantor" < "$base.inp" 2>/dev/null)
    expected=$(cat "$base.out")

    if [ "$got" = "$expected" ]; then
        echo "PASS $name"
        PASS=$((PASS + 1))
    else
        echo "FAIL $name  (esperat: '$expected', obtingut: '$got')"
        FAIL=$((FAIL + 1))
    fi
done

echo ""
echo "Resultat: $PASS passats, $FAIL fallats, $SKIP omesos"
[ "$FAIL" -eq 0 ]
