; ==============================================================================
; Onishi Layout (o24) - Official Validated Spec
; Connection verified via https://o24.works/layout/karabiner.json
; Toggle: Ctrl + Alt + S
; ==============================================================================

#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%
#SingleInstance Force

; Initial Notify
ToolTip, MODE: ONISHI o24 (Official), 10, 10
SetTimer, RemoveToolTip, -3000

; --- Onishi Layout Mapping (Official) ---

; Top Row (Physical Q-P)
q::q    ; Unchanged
w::l
e::u
r::,
t::.
y::f
u::w
i::r
o::y
p::p    ; Unchanged

; Home Row (Physical A-;)
a::e
s::i
d::a
f::o
g::-    ; Hyphen
h::k
j::t
k::n
l::s
sc027::h  ; Physical ; -> h

; Bottom Row (Physical Z-/)
z::z    ; Unchanged
x::x    ; Unchanged
c::c    ; Unchanged
v::v    ; Unchanged
b::sc027 ; Physical B -> ; (semicolon)
n::g
m::d
,::m
.::j
/::b

; Special Characters
; Physical Hyphen (-) -> Logical /
-::/

; Shifted mappings (Uppercase / Symbol consistency)
+q::Q
+w::L
+e::U
+r::<   ; Shift+,
+t::>   ; Shift+. (Use > for period shift?) usually > is shift+.
+y::F
+u::W
+i::R
+o::Y
+p::P

+a::E
+s::I
+d::A
+f::O
+g::_   ; Shift-Hyphen (Underscore)
+h::K
+j::T
+k::N
+l::S
+sc027::H

+z::Z
+x::X
+c::C
+v::V
+b::+sc027 ; Shift-; -> + (JIS) or : (US)? usually +
+n::G
+m::D
+,::M
+.::J
+/::B

+-::?   ; Shift-/ -> ?

; --- Control Logic ---

^!s::
Suspend
if (A_IsSuspended) {
    ToolTip, MODE: QWERTY (Active), 10, 10
} else {
    ToolTip, MODE: ONISHI o24 (Official), 10, 10
}
SetTimer, RemoveToolTip, -2000
return

; Force Exit (Restore QWERTY permanently)
^!q::
ExitApp
return

RemoveToolTip:
ToolTip
return
