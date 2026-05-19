# Decisions de Disseny — Intèrpret Cantorià
> Registre de decisions arquitectòniques (ADR) del projecte GEI-LP 2025-2026 Q2

---

## Índex

- [ADR-001 — Separació en mòduls](#adr-001)
- [ADR-002 — Representació de funcions com a callables Python](#adr-002)
- [ADR-003 — Codificació interna de parelles a les primitives](#adr-003)
- [ADR-004 — Estratègia de encode_list](#adr-004)
- [ADR-005 — Regla main_dir separada a la gramàtica](#adr-005)
- [ADR-006 — DOC com a token del Lexer](#adr-006)
- [ADR-007 — Tots els fitxers `.cantor` a `tests/`](#adr-007)
- [ADR-008 — Resolució d'imports relativa al fitxer actual](#adr-008)
- [ADR-009 — `set` per evitar imports duplicats](#adr-009)
- [ADR-010 — Gestió de definicions duplicades amb warning](#adr-010)

---

## ADR-001 — Separació en mòduls {#adr-001}

**Fase:** 0 i 1
**Estat:** ✅ Acceptada

### Context
Cal decidir com organitzar el codi Python de l'intèrpret.

### Decisió
Tres fitxers amb responsabilitats ben separades:

| Fitxer | Responsabilitat |
|--------|----------------|
| `cantor_math.py` | Matemàtica pura: `pi`, `unpi`, `encode_list` |
| `visitor.py` | Lògica de l'intèrpret: visitar l'AST i construir funcions |
| `cantor.py` | Orquestració: parsejar, visitar, llegir stdin, imprimir |

### Motiu
- **Testabilitat:** `cantor_math.py` es pot testar de forma completament independent
- **Llegibilitat:** cada fitxer té una única responsabilitat clara (principi SRP)
- **Mantenibilitat:** canvis a la gramàtica no afecten la matemàtica i viceversa

### Alternatives descartades
- Tot en un sol fitxer `cantor.py` — descartada per dificultar els tests i la llegibilitat

---

## ADR-002 — Representació de funcions com a callables Python {#adr-002}

**Fase:** 1
**Estat:** ✅ Acceptada

### Context
Cal decidir com representar internament les funcions cantorianes durant l'execució.

### Decisió
Cada funció cantoriana es representa com un **callable Python** (funció o lambda) emmagatzemat en un diccionari:

```python
self.functions: dict[str, Callable[[int], int]]
```

El visitador construeix aquests callables en temps de visita i els guarda per nom. Quan cal executar una funció, simplement es crida `self.functions[name](input)`.

### Motiu
- **Naturalitat:** `comp f g` és literalment `lambda x: f(g(x))` en Python
- **Simplicitat:** no cal cap estructura intermèdia (AST propi, bytecode, etc.)
- **Lazy evaluation:** les funcions es construeixen una vegada i es poden cridar múltiples vegades

### Alternatives descartades
- Construir un AST propi i interpretar-lo en cada crida — més complex i sense benefici per a aquest llenguatge
- Usar classes per representar cada tipus de funció — més verbós sense guany significatiu

---

## ADR-003 — Codificació interna de parelles a les primitives {#adr-003}

**Fase:** 1
**Estat:** ✅ Acceptada

### Context
Les funcions `add`, `mul` i `diff` reben una parella codificada `<x.y>`. Cal decidir on es fa el `unpi`.

### Decisió
Les funcions predefinides fan `unpi` **internament**:

```python
'add': lambda z: (lambda x, y: x + y)(*unpi(z)),
```

El caller simplement passa el valor codificat i no sap res de la descodificació.

### Motiu
- **Encapsulació:** el caller no ha de conèixer els detalls interns de cada funció
- **Consistència:** totes les funcions cantorianes tenen la mateixa signatura `int -> int`

### Alternatives descartades
- Fer `unpi` al visitador abans de cridar la funció — trenca la uniformitat de la signatura

---

## ADR-004 — Estratègia de encode_list {#adr-004}

**Fase:** 1
**Estat:** ✅ Acceptada

### Context
L'entrada del programa és una llista de naturals per stdin. Cal codificar-la en un sol natural per passar-la a la funció `main`.

### Decisió
Fold per la **dreta** amb `pi`, recursivament:

```python
encode_list([1, 3, 2]) = pi(1, pi(3, 2)) = pi(1, 17) = 188
```

Casos base:
- Llista buida → `0`
- Llista d'un element → l'element mateix

### Motiu
- Coincideix exactament amb l'especificació de l'enunciat
- El fold per la dreta permet recuperar els elements en ordre natural amb `fst` i `snd` encadenats

### Alternatives descartades
- Fold per l'esquerra — produiria una codificació diferent incompatible amb l'enunciat

---

## ADR-005 — Regla main_dir separada a la gramàtica {#adr-005}

**Fase:** 1
**Estat:** ✅ Acceptada

### Context
La directiva `main nom_funció` podria ser una regla inline a `program` o una regla pròpia.

### Decisió
Regla separada `main_dir`:

```antlr
program  : main_dir definition* EOF ;
main_dir : MAIN ID ;
```

### Motiu
- **Extensibilitat:** a les fases posteriors s'afegiran `import` i `extended`. Amb regles separades, `program` creix de forma neta:

```antlr
program : main_dir extended_dir? import_dir* definition* EOF ;
```

- **Llegibilitat:** cada directiva té el seu propi nom semàntic a l'arbre

### Alternatives descartades
- Inline a `program` (`MAIN ID definition* EOF`) — més compacte però dificulta l'extensió futura

---

## ADR-006 — DOC com a token del Lexer {#adr-006}

**Fase:** 1
**Estat:** ✅ Acceptada

### Context
La documentació de cada funció té el format `[text lliure]`. Cal decidir si es tracta al Lexer o al Parser.

### Decisió
Token del **Lexer**:

```antlr
DOC : '[' ~[\]]* ']' ;
```

### Motiu
- El contingut és text lliure sense estructura interna rellevant per a l'intèrpret
- Tractar-ho al Lexer és més simple i eficient — el Parser no necessita analitzar el contingut
- El text de documentació no afecta l'execució del programa

### Alternatives descartades
- Regla del Parser amb caràcters individuals — innecessàriament complex per a text que no s'interpreta

---

## ADR-007 — Tots els fitxers `.cantor` a `tests/` {#adr-007}

**Fase:** 2
**Estat:** ✅ Acceptada

### Context
Cal decidir on guardar els fitxers `.cantor`. Hi havia dues opcions: tots a `tests/` (Opció A) o separar scripts de llibreria a `lib/` i tests a `tests/` (Opció B).

### Decisió
Tots els fitxers `.cantor` (tant scripts de test com de llibreria) van a `tests/`.

### Motiu
- **Simplicitat:** un sol lloc on buscar fitxers, sense lògica de resolució de múltiples carpetes
- **Consistència amb l'enunciat:** els `.cantor` van sempre acompanyats de `.inp` i `.out`, cosa que encaixa amb una única carpeta de tests
- **Evita complexitat innecessària:** amb `lib/` l'intèrpret hauria de buscar en múltiples paths

### Alternatives descartades
- **Opció B** (`tests/` + `lib/`) — descartada perquè complica la resolució de paths quan un script de `tests/` importa una llibreria de `lib/`

---

## ADR-008 — Resolució d'imports relativa al fitxer actual {#adr-008}

**Fase:** 2
**Estat:** ✅ Acceptada

### Context
Quan un script fa `import anterior`, cal decidir com es troba el fitxer `anterior.cantor` al sistema de fitxers.

### Decisió
Els imports es resolen sempre **relatius al directori del fitxer que fa l'import**, usant `os.path`:

```python
self.base_dir = os.path.dirname(os.path.abspath(filepath))
filepath = os.path.join(self.base_dir, name + '.cantor')
```

### Motiu
- **Portabilitat:** funciona independentment d'on s'executi el programa
- **Naturalitat:** és el comportament esperat — un fitxer busca els seus imports al costat seu
- **Sense hardcoding:** no cal hardcodejar cap carpeta (`tests/`, etc.) a l'intèrpret

### Alternatives descartades
- Hardcodejar `tests/` al codi — fràgil i no portable
- Buscar sempre des del directori de treball actual — falla si s'executa des d'una carpeta diferent

---

## ADR-009 — `set` per evitar imports duplicats {#adr-009}

**Fase:** 2
**Estat:** ✅ Acceptada

### Context
Amb imports recursius, és possible que un mateix fitxer sigui importat múltiples vegades (directament o transitivament). Cal evitar processar-lo més d'una vegada.

### Decisió
Mantenir un `set` de paths absoluts ja processats a `self.imported`:

```python
self.imported = set()

if filepath in self.imported:
    return
self.imported.add(filepath)
```

### Motiu
- **Correctesa:** evita redefinicions de funcions i bucles infinits en imports circulars
- **Eficiència:** lookup i insert en O(1)
- **Simplicitat:** el `set` és l'estructura de dades natural per a "conjunt de coses ja vistes"

### Alternatives descartades
- Llista amb `in` — funciona però lookup és O(n)
- No gestionar duplicats — causaria errors en imports transitius comuns

---

*Última actualització: Fase 2 completada*

---

## ADR-010 — Gestió de definicions duplicades amb warning {#adr-010}

**Fase:** 2
**Estat:** ✅ Acceptada

### Context
Cal decidir com actuar quan un `define` intenta redefinir una funció que ja existeix a `self.functions`, ja sigui una primitiva o una funció definida anteriorment.

### Decisió
Emetre un **warning per stderr** i continuar sobreescrivint la funció:

```python
def visitDefinition(self, ctx):
    name = ctx.ID().getText()
    if name in self.functions:
        print(f"Warning: la funció '{name}' ja està definida", file=sys.stderr)
    func = self.visitBody(ctx.body())
    self.functions[name] = func
```

### Motiu
- **L'enunciat diu** que el programa no ha de petar mai i que els errors semàntics tenen efecte indefinit — un warning és consistent amb això
- **Informatiu:** l'usuari és avisat sense aturar l'execució
- **Simplicitat:** no cal cap estructura addicional, el diccionari `self.functions` ja permet comprovar si la clau existeix

### Alternatives descartades
- **Error fatal** — massa estricte, contradiu el requisit de "no petar mai"
- **Sobreescriure silenciosament** — pot causar bugs difícils de detectar sense cap avís
- **Set separat** — innecessari, `self.functions` ja conté tota la informació needed