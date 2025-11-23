# Selector CLI Grammar Specification v1.0

## EBNF Grammar Definition

```ebnf
(* ============================================ *)
(* Selector CLI Grammar v1.0                   *)
(* Extended Backus-Naur Form (EBNF)           *)
(* ============================================ *)

(* Top Level *)
command = browser_command
        | scan_command
        | collection_command
        | query_command
        | visual_command
        | export_command
        | storage_command
        | utility_command
        ;

(* ============================================ *)
(* Browser Commands                            *)
(* ============================================ *)

browser_command = open_command
                | refresh_command
                | wait_command
                | navigation_command
                ;

open_command = "open" , url ;

refresh_command = "refresh" ;

wait_command = "wait" , number ;

navigation_command = "back" | "forward" ;

url = string ;

(* ============================================ *)
(* Scan Commands                               *)
(* ============================================ *)

scan_command = "scan" , [ scan_options ] ;

scan_options = element_types
             | "--deep"
             | "--shadow"
             | element_types , ",", element_types
             ;

element_types = element_type , { "," , element_type } ;

element_type = "input" | "button" | "a" | "select" | "textarea" | "*" ;

(* ============================================ *)
(* Collection Commands                         *)
(* ============================================ *)

collection_command = add_command
                   | remove_command
                   | clear_command
                   | keep_command
                   | unique_command
                   | set_operation
                   ;

add_command = "add" , target , [ where_clause ] ;

remove_command = "remove" , target , [ where_clause ] ;

clear_command = "clear" ;

keep_command = "keep" , ( where_clause | index_spec ) ;

unique_command = "unique" ;

set_operation = union_command
              | intersect_command
              | difference_command
              ;

union_command = "union" , "with" , target ;

intersect_command = "intersect" , where_clause ;

difference_command = "difference" , "with" , target ;

target = element_type
       | index_spec
       | "all"
       | "*"
       ;

(* ============================================ *)
(* Query Commands                              *)
(* ============================================ *)

query_command = list_command
              | show_command
              | count_command
              | stats_command
              | filter_command
              ;

list_command = ( "list" | "ls" ) , [ target ] , [ where_clause ] ;

show_command = "show" , [ show_target ] ;

show_target = index_spec
            | element_type , "[" , number , "]"
            | "collection"
            | empty
            ;

count_command = "count" ;

stats_command = "stats" ;

filter_command = "filter" , where_clause ;

(* ============================================ *)
(* Visual Commands                             *)
(* ============================================ *)

visual_command = highlight_command
               | unhighlight_command
               | blink_command
               ;

highlight_command = ( "highlight" | "hl" ) , [ highlight_target ] , [ highlight_options ] ;

unhighlight_command = ( "unhighlight" | "unhl" ) ;

blink_command = "blink" , ( index_spec | "collection" ) ;

highlight_target = index_spec
                 | element_type
                 | "collection"
                 | empty
                 ;

highlight_options = "--label"
                  | "--color=" , color
                  | "--label" , "--color=" , color
                  ;

color = "red" | "blue" | "green" | "yellow" | "orange" ;

(* ============================================ *)
(* Export Commands                             *)
(* ============================================ *)

export_command = export_stmt , [ redirect ] ;

export_stmt = "export" , export_type ;

export_type = "selectors"
            | "playwright"
            | "selenium"
            | "puppeteer"
            | "json"
            | "csv"
            | "yaml"
            | "collection"
            ;

redirect = ">" , filename ;

(* ============================================ *)
(* Storage Commands                            *)
(* ============================================ *)

storage_command = save_command
                | load_command
                | saved_command
                | delete_saved_command
                | import_command
                ;

save_command = "save" , identifier ;

load_command = "load" , identifier ;

saved_command = "saved" | "ls" , "saved" ;

delete_saved_command = "delete" , "saved" , identifier ;

import_command = "import" , "collection" , "<" , filename ;

(* ============================================ *)
(* Utility Commands                            *)
(* ============================================ *)

utility_command = variable_command
                | macro_command
                | history_command
                | help_command
                | exit_command
                ;

variable_command = set_variable | show_variables ;

set_variable = "set" , identifier , "=" , target , [ where_clause ] ;

show_variables = "vars" ;

macro_command = define_macro | run_macro | exec_script ;

define_macro = "macro" , identifier , "{" , command_list , "}" ;

run_macro = "run" , identifier ;

exec_script = "exec" , filename ;

command_list = command , { newline , command } ;

history_command = show_history
                | repeat_command
                | search_history
                ;

show_history = "history" , [ number ] ;

repeat_command = "!!" | "!" , number ;

search_history = "history" , "search" , string ;

help_command = "help" , [ identifier ] ;

exit_command = "exit" | "quit" | "q" ;

(* ============================================ *)
(* Where Clause                                *)
(* ============================================ *)

where_clause = "where" , condition ;

condition = simple_condition
          | compound_condition
          ;

simple_condition = field , operator , value
                 | unary_condition
                 ;

compound_condition = simple_condition , logic_operator , condition
                   | "(" , condition , ")"
                   ;

unary_condition = "has" , field
                | "not" , "(" , condition , ")"
                | field , "=" , boolean
                ;

field = "type"
      | "text"
      | "placeholder"
      | "name"
      | "id"
      | "class"
      | "value"
      | "index"
      | "tag"
      | "visible"
      | "enabled"
      | "disabled"
      | identifier
      ;

operator = "="
         | "!="
         | ">"
         | ">="
         | "<"
         | "<="
         | "contains"
         | "starts"
         | "ends"
         | "matches"
         ;

logic_operator = "and" | "or" ;

value = string | number | boolean ;

(* ============================================ *)
(* Index Specification                         *)
(* ============================================ *)

index_spec = single_index
           | multiple_indices
           | index_range
           ;

single_index = "[" , number , "]" ;

multiple_indices = "[" , number_list , "]" ;

index_range = "[" , number , "-" , number , "]" ;

number_list = number , { "," , number } ;

(* ============================================ *)
(* Terminals                                   *)
(* ============================================ *)

identifier = letter , { letter | digit | "_" | "-" } ;

string = '"' , { character - '"' } , '"'
       | "'" , { character - "'" } , "'"
       ;

number = digit , { digit } ;

boolean = "true" | "false" ;

filename = identifier , [ "." , identifier ] ;

letter = "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j"
       | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t"
       | "u" | "v" | "w" | "x" | "y" | "z"
       | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J"
       | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T"
       | "U" | "V" | "W" | "X" | "Y" | "Z"
       ;

digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;

character = ? any unicode character ? ;

newline = ? newline character ? ;

empty = ? empty string ? ;

(* ============================================ *)
(* Comments                                    *)
(* ============================================ *)

(* Single line comment starts with # *)
comment = "#" , { character - newline } , newline ;
```

---

## Grammar Examples

### Browser Commands
```
open https://example.com
refresh
wait 5
back
forward
```

### Scan Commands
```
scan
scan input
scan input, button
scan --deep
scan input, button --shadow
```

### Collection Commands
```
add input
add [1]
add [1,2,3]
add [1-5]
add input where type="email"
add button where text contains "Submit"
add * where id != ""

remove [1]
remove button where text="Cancel"

clear

keep where type="email"
keep [0,2,4]

unique
```

### Query Commands
```
list
list input
list button where type="submit"
ls

show
show [5]
show collection

count
stats

filter where type="email"
```

### Visual Commands
```
highlight
highlight [1,2,3]
highlight input
highlight collection
highlight --label
highlight --color=red
hl

unhighlight
unhl

blink [1]
blink collection
```

### Export Commands
```
export selectors
export playwright
export selenium
export json
export csv

export playwright > test.py
export json > data.json
```

### Storage Commands
```
save login-form
load login-form
saved
ls saved
delete saved login-form

import collection < saved.json
```

### Utility Commands
```
set email-input = input where type="email"
vars

macro login-flow {
    add input where type="email"
    add input where type="password"
    add button where text="Login"
    highlight
}

run login-flow

exec script.sel

history
history 10
!!
!5
history search "add input"

help
help add
exit
quit
q
```

### Complex Where Clauses
```
where type="email"
where type="email" and placeholder != ""
where text="Submit" or text="确定"
where (type="text" or type="email") and name != ""
where not (disabled=true)
where has id
where has placeholder
where visible=true
where class contains "btn"
where text starts "Submit"
where placeholder ends "邮箱"
where text matches "^Submit.*"
where index > 5
where index >= 0 and index < 10
```

---

## Token Categories

### Keywords
```
Browser:    open, refresh, wait, back, forward
Scan:       scan
Collection: add, remove, clear, keep, unique, union, intersect, difference
Query:      list, ls, show, count, stats, filter
Visual:     highlight, hl, unhighlight, unhl, blink
Export:     export
Storage:    save, load, saved, delete, import
Utility:    set, vars, macro, run, exec, history, help, exit, quit
Special:    where, with, all, collection, has, not
```

### Operators
```
Comparison: =, !=, >, >=, <, <=
String:     contains, starts, ends, matches
Logic:      and, or, not
```

### Literals
```
String:  "value", 'value'
Number:  0, 1, 42, 100
Boolean: true, false
```

### Delimiters
```
[ ]  - Index specification
( )  - Grouping
{ }  - Macro body
,    - Separator
>    - Redirect
<    - Input redirect
=    - Assignment
#    - Comment
```

---

## Precedence Rules

### Operator Precedence (Highest to Lowest)
```
1. ( )           - Grouping
2. not           - Logical NOT
3. =, !=, >, >=, <, <=, contains, starts, ends, matches
4. and           - Logical AND
5. or            - Logical OR
```

### Examples
```
where type="email" or type="text" and has placeholder
# Parsed as: (type="email") or ((type="text") and (has placeholder))

where (type="email" or type="text") and has placeholder
# Explicitly grouped
```

---

## Reserved Words

The following are reserved and cannot be used as identifiers:

```
open, refresh, wait, back, forward
scan, deep, shadow
add, remove, clear, keep, unique, union, intersect, difference
list, ls, show, count, stats, filter
highlight, hl, unhighlight, unhl, blink
export, save, load, saved, delete, import
set, vars, macro, run, exec, history, help, exit, quit
where, with, all, collection, has, not
and, or, true, false
input, button, select, textarea
type, text, placeholder, name, id, class, value, index, tag
visible, enabled, disabled
contains, starts, ends, matches
```

---

## Error Productions

### Syntax Errors
```
add input where           # Missing condition
add where type="email"    # Missing target
export > filename         # Missing export type
[1,2,]                   # Trailing comma
```

### Semantic Errors
```
add nonexistent-type      # Invalid element type
where nonexistent-field = "value"  # Invalid field
highlight --color=purple  # Invalid color
```

---

## Extension Points

The grammar is designed to be extensible:

1. **New Element Types**: Add to `element_type` production
2. **New Fields**: Add to `field` production
3. **New Operators**: Add to `operator` production
4. **New Commands**: Add new productions to `command`
5. **New Export Formats**: Add to `export_type` production

---

## Grammar Version History

**v1.0 (2025-11-22)**
- Initial grammar definition
- Core commands: browser, scan, collection, query, visual, export, storage, utility
- Where clause with compound conditions
- Index specifications: single, multiple, range
- Variable and macro support
- History and help commands
