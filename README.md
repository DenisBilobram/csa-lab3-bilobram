# csa-lab3-bilobram

- Билобрам Денис Андреевич, P3219
- `asm | risc | harv | mc -> hw | instr | struct | stream | port | cstr | prob1 | -`
- Базовый вариант.

## Содержание

1. [Язык программирования](#язык-программирования)
2. [Организация памяти](#организация-памяти)
3. [Система команд](#система-команд)
4. [Транслятор](#транслятор)
5. [Модель процессора](#модель-процессора)
6. [Тестирование](#тестирование)

<h2 id="язык-программирования">Язык программирования ASM</h2>

``` bnf
<program> ::= <data_section> <text_section>

<data_section> ::= ".data" {<data_definition>}*

<data_definition> ::= <label> ":" <data_value>

<data_value> ::= <string_literal> | <number>

<charing_literal> ::= <char_literal> {"," <char_literal>}*

<char_literal> ::= "'" <char> "'"

<number> ::= <digit> {<digit>}*

<text_section> ::= ".text" {<instruction>}*

<instruction> ::= <label> ":" <command> | <command>

<label> ::= <letter> {<letter> | <digit>}*

<command> ::= "MOV" <reg> "," <number>
            | "MOV" <reg> "," <reg>
            | "LOAD" <reg> "," <direct_address>
            | "LOAD" <reg> "," <indirect_address>
            | "STORE" <reg> "," <direct_address>
            | "STORE" <reg> "," <indirect_address>
            | "ADD" <reg> "," <reg> "," <reg>
            | "SUB" <reg> "," <reg> "," <reg>
            | "DIV" <reg> "," <reg> "," <reg>
            | "IDIV" <reg> "," <reg> "," <reg>
            | "MUL" <reg> "," <reg> "," <reg>
            | "INC" <reg>
            | "DEC" <reg>
            | "CMP" <reg> "," <reg>
            | "CMP" <reg> "," <number>
            | "JMP" <label>
            | "JZ" <label>
            | "JNZ" <label>
            | "HALT"
            | "OUT" <reg> "," <port>
            | "IN" <reg> "," <port>

<reg> ::= "R1" | "R2" | "R3"

<direct_address> ::= <number>

<indirect_address> ::= "(" <reg> ")"

<port> ::= <number>

<letter> ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" |  "i" | "j" | "k" | "l" | "m"
           | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z"
           | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M"
           | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z"

<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

<char> ::= <letter> | <digit> | <special_char>

<special_char> ::= "!" | "\"" | "#" | "$" | "%" | "&" | "'" | "(" | ")" | "*" | "+" | "," | "-" | "." | "/" | ":" | ";" | "<" | "=" | ">" | "?" | "@" | "[" | "\\" | "]" | "^" | "_" | "`" | "{" | "|" | "}" | "~"
```

### Описание семантики ASM


#### Последовательное выполнение
Выполнение программы происходит последовательно, команда за командой, начиная с первой инструкции в секции `.text` и продолжая до встречи команды `HALT` или другой команды управления потоком, такой как `JMP` или `JNZ`.

#### Безусловный и условные переходы
- **`JMP <label>`**: Безусловный переход к указанной метке.
- **`JNZ <label>`**: Условный переход к указанной метке, если флаг Zero не установлен.
- **`JZ <label>`**: Условный переход к указанной метке, если флаг Zero установлен.

### Области видимости

#### Глобальные данные
Все данные, объявленные в секции `.data`, имеют глобальную область видимости. Это означает, что они доступны для всех инструкций в секции `.text` на протяжении всей программы.

#### Метки
Метки, используемые в секции `.text`, определяют точки в программе, к которым можно перейти с помощью команд управления потоком. Метки имеют локальную область видимости в пределах программы, но могут быть использованы для переходов из любой точки секции `.text`.

### Виды литералов

#### Числовые литералы
- **Описание**: Целые числа, используемые для инициализации данных, адресации и арифметических операций.
- **Пример**:
  ```
  CONST_ONE: 1
  MOV R1, 1000
  ```

#### Посимвольные литералы
- **Описание**: Последовательности символов, хранящиеся в памяти и используемые для вывода.
- **Пример**:
  ```
  HELLO: 'H', 'e', 'l', 'l', 'o', 0
  ```

<h2 id="организация-памяти">Организация памяти</h2>

### Модель памяти процессора

#### Машинное слово
- **Память данных**: 16 бит.
- **Память инструкций**: реализованна высокоуровневой структурой данных, машинное слово не определенно.

#### Варианты адресации
- **Косвенная адресация**: Адрес указывается в регистре. Формат: `(R1)` означает, что адрес содержится в регистре `R1`.
- **Прямая адресация**: Адрес указывается непосредственно. Формат: `100` означает, что данные находятся по адресу `100`.

### Механика отображения программы и данных на процессор
```
+----------------------+
|      Registers       |
+----------------------+
| R1                   |
| R2                   |
| R3                   |
+----------------------+

+-----------------------+
|   Instruction memory  |
+-----------------------+
| 00 : program start    |
| ...                   |
| n  : HALT             |
| ...                   |
+-----------------------+

+-----------------------+
|      Data memory      |
+-----------------------+
| 00 : num literal      |
| ...                   |
| l  : variable 1       |
| l+1: variable 2       |
| ...                   |
| c  : char literal     |
| ...                   |
+-----------------------+
```

#### Виды памяти и регистров, доступные программисту
- **Регистры общего назначения**: R1, R2, R3.
- **Память данных**: Используется для хранения данных, объявленных в секции `.data`.

#### Input/Output
- **Чтение и вывод** осуществляется через input/output буферы, к которым подключены порты.
- **Номер порта** ввода/вывода берётся из регистра OR.

<h2 id="система-команд">Система комад:</h2>

#### Команда `MOV`
- **Семантика**: Перемещает данные из одного регистра в другой или число в регистр.
- **Пример**:
  ```MOV R1, 1000    ; R1 = 1000
  MOV R2, R1      ; R2 = R1 (то есть R2 = 1000)
  ```

#### Команда `LOAD`
- **Семантика**: Загружает данные из памяти по указанному адресу в регистр.
- **Пример**:
  ```LOAD R1, (R2)   ; R1 = память[адрес, указанный в R2]
  LOAD R3, 50     ; R3 = память[адрес 50]
  ```
#### Команда `STORE`
- **Семантика**: Сохраняет данные из регистра в память по указанному адресу.
- **Пример**:
  ```STORE R1, (R2)  ; память[адрес, указанный в R2] = R1
  STORE R3, 100   ; память[адрес 100] = R3
  ```

#### Команда `ADD`
- **Семантика**: Складывает значения из двух регистров и сохраняет результат в третий регистр.
- **Пример**:
  ```
  ADD R1, R2, R3  ; R1 = R2 + R3
  ```

#### Команда `SUB`
- **Семантика**: Вычитает значение одного регистра из другого и сохраняет результат в третий регистр.
- **Пример**:
  ```
  SUB R1, R2, R3  ; R1 = R2 - R3
  ```

#### Команда `IDIV`
- **Семантика**: Выичсляет остаток от отделения первого регистра на воторой и записывает в третий регистр.
- **Пример**:
  ```
  IDIV R1, R2, R3  ; R1 = R2 % R3
  ```

#### Команда `DIV`
- **Семантика**: Целочисленно делит первый регистр на второй и сохраняет результат в третий регистр.
- **Пример**:
  ```
  DIV R1, R2, R3  ; R1 = R2 / R3
  ```

#### Команда `MUL`
- **Семантика**: Перемножает два регистра и сохраняет результат в третий регистр.
- **Пример**:
  ```
  MUL R1, R2, R3  ; R1 = R2 * R3
  ```

#### Команда `INC`
- **Семантика**: Увеличивает значение регистра на единицу.
- **Пример**:
  ```
  INC R1          ; R1 = R1 + 1
  ```

#### Команда `CMP`
- **Семантика**: Сравнивает значения двух регистров и устанавливает флаг состояния Zero, если значения равны.
- **Пример**:
  ```
  CMP R1, R2      ; Устанавливает флаг Zero, если R1 == R2
  ```

#### Команда `JMP`
- **Семантика**: Безусловный переход к указанной метке.
- **Пример**:
  ```
  JMP START       ; Переход к метке START
  ```

#### Команда `JZ`
- **Семантика**: Условный переход к указанной метке, если флаг Zero установлен.
- **Пример**:
  ```
  JZ LOOP       ; Переход к метке LOOP, если флаг Zero установлен
  ```

#### Команда `JNZ`
- **Семантика**: Условный переход к указанной метке, если флаг Zero не установлен.
- **Пример**:
  ```
  JNZ LOOP       ; Переход к метке LOOP, если флаг Zero не установлен
  ```

#### Команда `HALT`
- **Семантика**: Останавливает выполнение программы.
- **Пример**:
  ```
  HALT            ; Остановка программы
  ```

#### Команда `OUT`
- **Семантика**: Выводит данные из регистра на указанный порт.
- **Пример**:
  ```
  OUT R1, 1       ; Вывод значения из R1 на порт 1
  ```

#### Команда `IN`
- **Семантика**: Загружает данные с указанного порта в регистр.
- **Пример**:
  ```
  IN R1, 2        ; Загрузка значения с порта 2 в R1
  ```

<h2 id="транслятор">Транслятор</h2>

Этот транслятор предназначен для перевода ассемблерного кода в JSON формат. Он читает исходный ассемблерный файл, парсит его, обрабатывает и сохраняет результат в JSON файл.

### Интерфейс командной строки

Транслятор запускается из командной строки с указанием входного файла (файла с ассемблерным кодом) и выходного файла (файла, в который будет записан JSON).

Пример использования:

    python translator.py input.asm output.json

### Принципы работы транслятора

Транслятор выполняет следующие этапы:

1. **Чтение и разделение секций `.data` и `.text`**:
    - Ассемблерный код разделяется на секции `.data` и `.text`. Секция `.data` содержит данные, а секция `.text` - команды.

2. **Обработка секции `.data`**:
    - Каждая строка секции `.data` обрабатывается для извлечения меток и значений.
    - Значения могут быть зарезервированы (`RESERVE`) или представлять собой последовательности символов и чисел.
    - Значения добавляются в список данных, и соответствующие метки запоминаются с их адресами.

3. **Обработка секции `.text`**:
    - Каждая строка секции `.text` обрабатывается для извлечения команд и их аргументов.
    - Если строка содержит метку, эта метка запоминается с текущим адресом команды.
    - Команды добавляются в список текстовых инструкций.

4. **Замена меток на адреса и формирование инструкций**:
    - В командах текстовой секции метки заменяются на их адреса.
    - Форматируются аргументы команд в зависимости от их типа (регистр, число, косвенный адрес).

5. **Генерация JSON**:
    - Сформированные данные и текстовые инструкции преобразуются в JSON формат.

### Пример работы

Пример входного ассемблерного кода:
```
.data
hello: 'H', 'e', 'l', 'l', 'o', '\n', 0

.text
START:
    MOV R1, hello
PRINT:
    LOAD R2, (R1)
    CMP R2, 0
    JZ END
    OUT R2, port1_out
    INC R1
    JMP PRINT
END:
    HALT
```
После обработки этот код преобразуется в следующий JSON:
```
{"data": [72, 101, 108, 108, 111, 10, 0], "text": [{"opcode": "MOV", "args": [{"reg": "R1"}, {"number": "0"}]}, {"opcode": "LOAD", "args": [{"reg": "R2"}, {"indirect_address": "R1"}]}, {"opcode": "CMP", "args": [{"reg": "R2"}, {"number": "0"}]}, {"opcode": "JZ", "args": [{"number": "7"}]}, {"opcode": "OUT", "args": [{"reg": "R2"}]}, {"opcode": "INC", "args": [{"reg": "R1"}]}, {"opcode": "JMP", "args": [{"number": "1"}]}, {"opcode": "HALT", "args": []}]}
```
Реализован в модуле [транслятора](translator.py).

<h2 id="модель-процессора">Модель процессора</h2>

### Control Unit

![Control Unit](resources/control_unit.png)

### Data Path
![Data Path](resources/data_path.png)

Программная реализация [Control Unit](control_unit.py) и [Data Path](data_path.py).


### Микропрограммное управление

#### Осуществляется при помощи:
- **Control logic**: Получает микрокоманду и отправляет управляющие сигналы элементам Data Path и Control Unit.

- **Control Store**: Хранит все микропрограммы. Получает адрес микрокоманды, считывает микрокоманду и отправляет её в Control Logic.

- **μPC**: Хранит адрес текущей микропрограммы.

- **Instruction Decoder**: Декодирует команду, определяя адрес начала микропрограммы, а так же извлекает численный аргумент из команды.

#### Микрокоманда состоит из 33 управляющих битов:

| Bit Pos      | Control Sginal          | Description                  |
|--------------|----------------|---------------------------------------|
| 0            | latch_ip       | Латчирование значения IP              |
| 1            | sel_ip         | Выбор между инкрементом IP и загрузкой операнда текущей команды |
| 2            | latch_ir       | Латчирование значения IR              |
| 3            | latch_mc_addr  | Латчирование значения μPC             |
| 4-5          | sel_mc_addr    | Выбор между инкрементом μPC, загрузкой следующей микропрограммы и обнулением μPC |
| 6            | read_mc        | Чтение микрокоманды из Control Store  |
| 7            | latch_r1       | Латчирование значения в R1            |
| 8            | latch_r2       | Латчирование значения в R2            |
| 9            | latch_r3       | Латчирование значения в R3            |
| 10-11        | sel_op_1       | Выбор первого операнда ALU            |
| 12-13        | sel_op_2       | Выбор второго операнда ALU            |
| 14-16        | operation      | Выбор операции ALU                    |
| 17           | start_decode   | Начать декодирование инструкции       |
| 18           | sel_addr       | Выбор адреса для AR                   |
| 19           | latch_addr     | Латчирование значения в AR            |
| 20           | mem_read       | Чтение из памяти                      |
| 21           | mem_write      | Запись в память                       |
| 22           | out_buf_write  | Вывод через порт указанный в OR       |
| 23           | out_buf_next   | Добавить следующее значение в буфер   |
| 24           | inp_buf_read   | Чение через порт указанный в OR       |
| 25           | inp_buf_next   | Перейти к следующему значению буфера  |
| 26           | latch_dr       | Латчирование значения в DR            |
| 27-28        | sel_r_read     | Выбор из R1-R3 на выход MUX2          |
| 29-31        | sel_r_write    | Выбор из 5 входов на выход MUX1       |
| 32           | latch_or       | Латчирование значения в OR            |

#### Значения управляюших сигналов в микрокоманде:

| Bit Pos | Value | Meaning                              |
|---------|-------|--------------------------------------|
| 0       | 1     | Защёлкнуть IP                        |
| 1       | 0     | Инкремент IP                         |
| 1       | 1     | operand -> IP                        |
| 2       | 1     | Защёлкнуть IR                        |
| 3       | 1     | Защёлкнуть μPC                       |
| 4-5     | 00    | Инкремент μPC                        |
| 4-5     | 01    | Загрузить новый адрес в μPC          |
| 4-5     | 10    | Обнулить μPC                         |
| 6       | 1     | Чтение микрокоманды по адресу из μPC |
| 7       | 1     | Защёлкнуть R1                        |
| 8       | 1     | Защёлкнуть R2                        |
| 9       | 1     | Защёлкнуть R3                        |
| 10-11   | 00    | Значение R1 в первый операнд ALU     |
| 10-11   | 01    | Значение R2 в первый операнд ALU     |
| 10-11   | 10    | Значение R3 в первый операнд ALU     |
| 12-13   | 00    | Значение R1 в второй операнд ALU     |
| 12-13   | 01    | Значение R2 в второй операнд ALU     |
| 12-13   | 10    | Значение R3 в второй операнд ALU     |
| 12-13   | 11    | Значение OP в второй операнд ALU     |
| 14-16   | 000    | Операция сложения в ALU              |
| 14-16   | 001    | Операция вычитания в ALU             |
| 14-16   | 010    | Операция получения остатка от деления в ALU |
| 14-16   | 011    | Операция деления в ALU               |
| 14-16   | 100    | Операция умножения в ALU               |
| 14-16   | 101    | Операция инкремента первого операнда в ALU               |
| 14-16   | 110    | Операция декремента первого операнда в ALU               |
| 17      | 1     | Начать декодировать инструкцию       |
| 18      | 0     | Значение аргумента на выход MUX3     |
| 18      | 1     | Значение MUX2 на выход MUX3          |
| 19      | 1     | Защёлкнуть AR                        |
| 20      | 1     | Чтение из памяти                     |
| 21      | 1     | Запись в память                      |
| 22      | 1     | Вывод через порт указанный в OR      |
| 23      | 1     | Добавить значение в выходной буфер   |
| 24      | 1     | Чение через порт указанный в OR      |
| 25      | 1     | Следующее значение входного буфреа   |
| 26      | 1     | Защёлкнуть значение в DR             |
| 27-28   | 00    | Значение R1 на выход MUX2            |
| 27-28   | 01    | Значение R2 на выход MUX2            |
| 27-28   | 10    | Значение R3 на выход MUX2            |
| 29-31   | 000   | Результат ALU на выход MUX1          |
| 29-31   | 001   | OR на выход MUX1                     |
| 29-31   | 010   | input buffer на выход MUX1           |
| 29-31   | 011   | DR на выход MUX1                     |
| 29-31   | 100   | Выход MUX2 на выход MUX1             |
| 32      | 1     | Защёлкнуть значение в OR             |

#### Инструкции декодированные в микропрограммы:

Программная реализация памяти микропрограмм и устройств микропрограммного управления находится в [микропрограммном модуле](microcode.py).
В памяти помимо микропрограмм для каждой инструкции присутствует специальная микропрограмма для выбора инструкции. Она располагается по адресу 0, именно с неё начинает работу Control Unit, и после выполнения каждой команды возваращается к этой микропрограмме.

<h2 id="тестирование">Тестирование</h2>


Этот проект использует непрерывную интеграцию (CI) с помощью GitHub Actions для автоматического запуска линтинга и тестов при каждом пуше или пул-реквесте.

### Тесты

Golden tests реализованны в файле [тестов](golden_asm_test.py), данные для проверки хранятся [здесь](golden).

### Линтер

Линтер используется для проверки стиля кода и поиска потенциальных ошибок. В этом проекте используется `Ruff` для линтинга Python-кода.

#### Настройка линтера

Конфигурация для линтера `Ruff` находится в файле [pyproject](pyproject.toml).

## Статистика
<div style="overflow-x: auto;">

| ФИО                            | алг   | LoC | code байт | code инстр. | инстр. | такт. | вариант |
|--------------------------------|-------|-----|-----------|-------------|--------|-------|---------|
|Билобрам Денис Андреевич        | hello | 15  |  -        |      8      |   41   | 141   | asm \| risc \| harv \| mc \| instr \| struct \| stream \| port \| cstr \| prob1 \| - |
|Билобрам Денис Андреевич        | cat   | 5   |  -        |      3      |   19   | 56    | asm \| risc \| harv \| mc \| instr \| struct \| stream \| port \| cstr \| prob1 \| - |
|Билобрам Денис Андреевич        | hello_user_name | 54 | -|      34     |   238  | 824   | asm \| risc \| harv \| mc \| instr \| struct \| stream \| port \| cstr \| prob1 \| - |
|Билобрам Денис Андреевич        | prob1 | 61  |  -        |      46     |   13021| 45696 | asm \| risc \| harv \| mc \| instr \| struct \| stream \| port \| cstr \| prob1 \| - |

</div>