; ==============================================================================
; VECTIS NEURAL INTERFACE - Onishi o24 Layout Manager (AutoHotkey v2)
; ==============================================================================
; Description: Modern AutoHotkey v2 implementation of Onishi o24 layout.
;              Features a sleek On-Screen Display (OSD) and sound signals.
; Toggle: Ctrl + Alt + S
; Exit: Ctrl + Alt + Q
; ==============================================================================

#Requires AutoHotkey v2.0
#SingleInstance Force
SetWorkingDir(A_ScriptDir)

; --- Global State ---
global IsOnishi := true
global StatusGui := unset

; --- Tray Menu ---
A_TrayMenu.Delete() ; Clear default
A_TrayMenu.Add("Restore QWERTY (Toggle)", (*) => ToggleOnishi())
A_TrayMenu.Add("Exit Script (Full QWERTY)", (*) => ExitApp())
A_TrayMenu.Default := "Restore QWERTY (Toggle)"

; --- UI Layout Setup ---
CreateOSD() {
    global StatusGui
    StatusGui := Gui("+AlwaysOnTop -Caption +ToolWindow", "OnishiStatus")
    StatusGui.BackColor := "111111"
    StatusGui.SetFont("s10 c00FFCC bold", "Link") ; Modern sans-serif fallback
    StatusGui.Add("Text", "vStatusDisplay", "MODE: ONISHI o24 [ACTIVE]")
    StatusGui.Show("x10 y10 NoActivate")
    WinSetTransparent(200, StatusGui)
    SetTimer(() => StatusGui.Hide(), -3000)
}

; Initial Setup
CreateOSD()
SoundBeep(750, 200)

; ==============================================================================
; Mappings (o24 Official Specification)
; ==============================================================================

#HotIf IsOnishi

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

#HotIf

; ==============================================================================
; Control Logic
; ==============================================================================

; --- Toggle Mode ---
^!s::ToggleOnishi()

ToggleOnishi() {
    global IsOnishi := !IsOnishi
    UpdateStatus()
}

; --- Force Exit ---
^!q::ExitApp()

; --- UI Update Logic ---
UpdateStatus() {
    global StatusGui, IsOnishi
    StatusGui.Show("x10 y10 NoActivate")
    if (IsOnishi) {
        StatusGui["StatusDisplay"].Value := "MODE: ONISHI o24 [ACTIVE]"
        StatusGui.BackColor := "111111"
        SoundBeep(750, 100)
    } else {
        StatusGui["StatusDisplay"].Value := "MODE: QWERTY [STANDARD]"
        StatusGui.BackColor := "333333"
        SoundBeep(500, 100)
    }
    SetTimer(() => StatusGui.Hide(), -2000)
}
