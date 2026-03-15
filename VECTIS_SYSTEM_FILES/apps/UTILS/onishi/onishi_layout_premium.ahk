; ==============================================================================
; VECTIS NEURAL INTERFACE - Onishi o24 Layout Manager
; ==============================================================================
; Description: High-performance Onishi o24 layout implementation with 
;              Visual On-Screen Display (OSD) and sound feedback.
; Toggle: Ctrl + Alt + S
; Exit: Ctrl + Alt + Q
; ==============================================================================

#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%
#SingleInstance Force
#MaxHotkeysPerInterval 200

; --- Global State ---
IsOnishi := True

; --- UI Layout Setup ---
CustomColor := "00FFCC"
Gui, +LastFound +AlwaysOnTop -Caption +ToolWindow
Gui, Color, 111111
Gui, Font, s10 c%CustomColor% bold, Share Tech Mono
Gui, Add, Text, vStatusDisplay, MODE: ONISHI o24 [ACTIVE]
Gui, Show, x10 y10 NoActivate
WinSet, Transparent, 200

SetTimer, RemoveUI, -3000

; --- Sound Feedback ---
SoundBeep, 750, 200

Return ; End of Auto-execute

; ==============================================================================
; Mappings (o24 Official Specification)
; ==============================================================================

#If (IsOnishi)

; Top Row
q::q
w::l
e::u
r::,
t::.
y::f
u::w
i::r
o::y
p::p

; Home Row
a::e
s::i
d::a
f::o
g::-   ; Hyphen
h::k
j::t
k::n
l::s
sc027::h ; physical ;

; Bottom Row
z::z
x::x
c::c
v::v
b::sc027 ; physical B -> ;
n::g
m::d
,::m
.::j
/::b

; Special
-::/

; --- Shifted ---
+q::Q
+w::L
+e::U
+r::<
+t::>
+y::F
+u::W
+i::R
+o::Y
+p::P

+a::E
+s::I
+d::A
+f::O
+g::_
+h::K
+j::T
+k::N
+l::S
+sc027::H

+z::Z
+x::X
+c::C
+v::V
+b::+sc027
+n::G
+m::D
+,::M
+.::J
+/::B
+-::?

#If

; ==============================================================================
; Control Logic
; ==============================================================================

; --- Toggle Mode ---
^!s::
IsOnishi := !IsOnishi
GoSub, ShowStatus
Return

; --- Force Exit ---
^!q::
SoundBeep, 500, 300
ExitApp
Return

; --- UI Update Logic ---
ShowStatus:
Gui, Show, x10 y10 NoActivate
if (IsOnishi) {
    GuiControl,, StatusDisplay, MODE: ONISHI o24 [ACTIVE]
    Gui, Color, 111111
    SoundBeep, 750, 100
} else {
    GuiControl,, StatusDisplay, MODE: QWERTY [STANDARD]
    Gui, Color, 333333
    SoundBeep, 500, 100
}
SetTimer, RemoveUI, -2000
Return

RemoveUI:
Gui, Hide
Return
