# Intèrpret Cantorià — GEI-LP 2025-2026 Q2

Implementació d'un intèrpret per a un llenguatge de programació minimalista basat en les **funcions d'aparellament de Cantor**. En aquest llenguatge totes les funcions operen sobre un únic natural; múltiples arguments s'empaqueten en un sol natural mitjançant la funció de Cantor `π(x, y)`.

El llenguatge permet definir funcions a partir d'un conjunt de primitives i constructors, i en mode *extended* afegeix recursivitat general (μ) i primitiva (`primrec`).

## Instal·lació

Cal tenir instal·lats:

- Python 3.12+
- Java OpenJDK 11+ (per generar el parser via ANTLR)

El jar d'ANTLR 4.13.2 ja s'inclou al projecte. Només cal instal·lar el runtime Python:

```bash
pip install antlr4-python3-runtime==4.13.2
```

## Ús

La primera vegada, cal generar els fitxers del parser:

```bash
make
```

Per executar un programa:

```bash
echo "<arguments>" | python3 cantor.py tests/<programa>.cantor
```

Múltiples arguments s'escriuen separats per espai i s'empaqueten automàticament amb `π`.

Alguns exemples:

```bash
echo "3 2" | python3 cantor.py tests/suma.cantor        # → 5
echo "5"   | python3 cantor.py tests/factorial.cantor   # → 120
echo "7"   | python3 cantor.py tests/fibonacci.cantor   # → 21
echo "7 2" | python3 cantor.py tests/mod.cantor         # → 1
echo "4"   | python3 cantor.py tests/even.cantor        # → 1
echo "5 3" | python3 cantor.py tests/cond.cantor        # → 5
```

## Codi

### Funcionament general

El projecte es divideix en tres fitxers Python amb responsabilitats ben separades:

- `cantor_math.py` — Matemàtica pura: `pi`, `unpi` i `encode_list`. Sense cap dependència de l'ANTLR.
- `visitor.py` — Visitador de l'AST: construeix les funcions Python a partir de les definicions del programa.
- `cantor.py` — Punt d'entrada: orquestra el flux complet (parsejar, visitar, llegir stdin, imprimir).

Els fitxers `cantorLexer.py`, `cantorParser.py`, `cantorListener.py` i `cantorVisitor.py` els genera ANTLR a partir de `cantor.g4` en executar `make`.

### Gramàtica (`cantor.g4`)

Un programa cantorià té sempre l'estructura:

```
main <nom_funció>
[extended]
[import <mòdul>]*
[define <nom> [doc] <cos>]*
```

La directiva `main` indica quina funció s'executa. La directiva `extended` és opcional i habilita els constructors avançats. Els `import` carreguen definicions d'altres fitxers `.cantor`. Cada `define` associa un nom a un cos, que és un dels constructors de la taula següent:

| Constructor | Sintaxi | Semàntica |
|-------------|---------|-----------|
| `pair`    | `pair f g`       | `x ↦ π(f(x), g(x))` |
| `comp`    | `comp f g`       | `x ↦ f(g(x))` |
| `compair` | `compair f g h`  | `x ↦ f(π(g(x), h(x)))` *(extended)* |
| `mu`      | `mu f`           | `x ↦ min{k : f(π(x,k)) ≠ 0}` *(extended)* |
| `primrec` | `primrec f g h`  | Recursió primitiva sobre `x` *(extended)* |

La documentació de cada funció s'escriu entre claudàtors (`[text lliure]`) i és ignorada per l'intèrpret.

### Mòdul matemàtic (`cantor_math.py`)

Conté les tres operacions fonamentals del llenguatge:

- `pi(x, y)` — Codifica la parella `(x, y)` en un natural via la fórmula de Cantor.
- `unpi(z)` — Inversa de `pi`: retorna `(x, y)`. Usa `math.isqrt` per precisió exacta amb enters grans.
- `encode_list(lst)` — Fold dret amb `pi`: `[a, b, c]` → `π(a, π(b, c))`. Cas base: llista buida → `0`.

### Visitador (`visitor.py`)

La classe `CantorVisitor` hereta de `cantorVisitor` (generada per ANTLR) i construeix les funcions del programa durant la visita de l'AST.

**Atributs:**

- `self.functions` — Diccionari `{nom: Callable[[int], int]}`. S'inicialitza amb les set primitives predefinides: `k_1`, `id`, `add`, `mul`, `diff`, `fst`, `snd`.
- `self.extended` — Flag booleà que s'activa si el programa declara `extended`.
- `self.imported` — `set` de paths absoluts ja processats, per evitar imports duplicats.
- `self.base_dir` — Directori base per resoldre imports relatius.

**Mètodes principals:**

- `visitProgram` — Activa `extended` si escau, processa imports i definicions en ordre, i retorna la funció `main`.
- `visitImport_dir` — Parseja el fitxer importat recursivament (sense processar el seu `main`) i afegeix les seves definicions a `self.functions`. Evita duplicats amb `self.imported`.
- `visitDefinition` — Crida `visitBody` i guarda el callable resultant a `self.functions`. Emet un warning per stderr si el nom ja existia.
- `visitBody` — Construeix el callable Python corresponent al constructor indicat:
  - `pair f g` → `lambda x: pi(f(x), g(x))`
  - `comp f g` → `lambda x: f(g(x))`
  - `compair f g h` → `lambda x: f(pi(g(x), h(x)))`
  - `mu f` → cerca lineal amb `itertools.count()`
  - `primrec f g h` → delega a `_make_primrec`
- `_make_primrec(f, g, h)` — Implementa la recursió primitiva. Manté una tupla acumulada interna `π(resultat_actual, resultat_anterior)` i retorna directament el primer element, de manera que l'usuari de `primrec` obté un natural directament.

### Punt d'entrada (`cantor.py`)

El driver llegeix el fitxer `.cantor` passat com a argument, el converteix en un `FileStream` i el passa al lexer `cantorLexer`, que genera tokens. El parser `cantorParser` construeix l'arbre sintàctic, que el `CantorVisitor` visita per obtenir la funció `main`. Finalment, es llegeix stdin, es codifica l'entrada amb `encode_list` i s'executa la funció.

Tant el lexer com el parser usen un `SyntaxErrorListener` personalitzat per reportar errors sintàctics per stderr amb línia i columna.

## Gestió d'errors

L'enunciat estableix que no es donaran errors semàntics, de tipus o d'execució, però el programa no ha de petar en cap cas.

- **Errors sintàctics** — Reportats per stderr amb línia i columna i finalitzen amb codi de sortida 1:
  ```
  Error sintàctic [3:5]: mismatched input 'foo' expecting ...
  ```
- **Fitxer no trobat** — Missatge clar per stderr si el fitxer `.cantor` principal o un importat no existeix.
- **Funció no definida** — Si `main` referencia un nom absent a `self.functions`.
- **Entrada invàlida** — Si stdin conté valors no enters.
- **Recursió excessiva** — `RecursionError` capturat per a programes amb profunditat molt gran.
- **Definicions duplicades** — Warning per stderr, l'última definició guanya.

## Jocs de proves

Els jocs de proves es troben a `tests/`. Cada script `.cantor` té un fitxer `.inp` amb l'entrada i un `.out` amb la sortida esperada.

Per executar tots els tests automàticament:

```bash
bash test.sh
```

Per comparar manualment la sortida d'un test:

```bash
python3 cantor.py tests/factorial.cantor < tests/factorial.inp | diff - tests/factorial.out
```

Scripts disponibles:

| Fitxer | `main` | Descripció |
|--------|--------|-----------|
| `suma.cantor` | `add` | Suma de dos naturals |
| `anterior.cantor` | `anterior` | Predecessor amb límit 0 |
| `signe.cantor` | `signe` | 0→0, resta→1 |
| `booleans.cantor` | `not` | `not`, `and`, `or` |
| `relacionals.cantor` | `lt` | `lt`, `gt`, `eq`, `neq` |
| `add3.cantor` | `add3` | Suma de tres elements |
| `div.cantor` | `div` | Divisió entera via `mu` |
| `mod.cantor` | `mod` | Residu |
| `even.cantor` | `even` | Paritat |
| `maxmin.cantor` | `max` | Màxim i mínim |
| `cond.cantor` | `max2` | Màxim via condicional |
| `factorial.cantor` | `factorial` | Factorial via `primrec` |
| `fibonacci.cantor` | `fibonacci` | Fibonacci via `primrec` |

Els fitxers `test_*.cantor` proporcionen casos addicionals: casos límit a zero, casos falsos per a les funcions relacionals i booleanes, i tests per a `min`, `even` imparell, divisió exacta, etc.

## Decisions de disseny

**Tres mòduls amb responsabilitats separades** — `cantor_math.py` conté la matemàtica pura independent de l'ANTLR; `visitor.py` construeix les funcions Python a partir de l'AST; `cantor.py` orquestra el flux complet. Cada mòdul es pot llegir i testar de forma independent (principi SRP).

**Funcions com a callables Python** — Cada funció cantoriana es representa com un `Callable[[int], int]` emmagatzemat per nom a `self.functions`. `comp f g` es tradueix literalment a `lambda x: f(g(x))`, sense cap AST intermedi ni estructura addicional. Les funcions es construeixen una sola vegada en temps de visita.

**`unpi` intern a les primitives** — `add`, `mul`, `diff`, `fst` i `snd` fan la descodificació de la parella internament, de manera que totes les funcions cantorianes comparteixen la mateixa signatura `int → int` i el caller no necessita gestionar l'empaquetament.

**`encode_list` per fold dret** — L'entrada `a b c` s'encoda com `π(a, π(b, c))`, consistent amb l'enunciat i recuperable en ordre natural amb `fst` i `snd` encadenats.

**`DOC` com a token del lexer** — El text `[...]` és opac per a l'intèrpret; tractar-lo al lexer evita regles innecessàries al parser i simplifica la gramàtica.

**Imports relatius al fitxer actual** — Quan `foo.cantor` fa `import bar`, es busca `bar.cantor` al mateix directori que `foo.cantor` (via `os.path.dirname`), independentment d'on s'executi el programa. Imports duplicats s'ignoren amb un `set` de paths absoluts ja processats.

**`extended` activat abans dels imports** — A `visitProgram`, el flag `self.extended` s'activa abans de processar cap import. Això garanteix que les definicions dels fitxers importats que usen `compair`, `mu` o `primrec` es construeixin correctament.

**`mu` amb `itertools.count()`** — La cerca lineal no imposa cap límit artificial. Si el predicat mai es satisfà, el programa entra en bucle infinit, que és l'efecte indefinit establert per l'enunciat per a errors semàntics.

**`primrec` retorna `fst` de la tupla acumulada** — Internament, la funció auxiliar `s(x)` acumula `π(resultat_actual, resultat_anterior)`, però `_make_primrec` retorna directament `fst(s(x))`. L'usuari obté un natural sense haver de fer `comp fst` al `.cantor`.

**`isqrt` en lloc de `sqrt` a `unpi`** — `math.sqrt` perd precisió amb enters grans (els que genera `primrec` per Fibonacci). `math.isqrt` opera amb enters arbitràriament grans i és exacte.

## Limitacions

Totes les funcionalitats requerides estan implementades. No hi ha parts de la pràctica sense realitzar ni errors coneguts.

## Autor

Marc Rams Estrada
`marc.rams.estrada@gmail.com`
