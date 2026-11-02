#Requires AutoHotkey v2.0
#SingleInstance Force
SetTitleMatchMode 3

; Paths work on any PC: the .pyw must sit in the same folder as this script.
PyFile := A_ScriptDir "\TodoList.pyw"
PyW    := EnvGet("LOCALAPPDATA") "\Programs\Python\Python312\pythonw.exe"
if !FileExist(PyW)
    PyW := "pyw.exe"        ; fall back to the Python launcher (uses your default Python)
TodoWin := "My Tasks ahk_exe pythonw.exe"

; F2: not open -> open. Open and in front -> close. Open but behind -> bring forward.
F2::
{
    if !(hwnd := WinExist(TodoWin))
    {
        if !FileExist(PyFile)
        {
            MsgBox("Can't find:`n" PyFile, "To-do list")
            return
        }
        Run('"' PyW '" "' PyFile '"', A_ScriptDir)
        return
    }
    if InFront(hwnd)
    {
        ; Ask Python to close (it shuts any open menu/dialog first, then saves)
        PostMessage 0x8012, 0, 0, , hwnd
        if !WinWaitClose(hwnd, , 2)
            WinClose(hwnd)
    }
    else
        WinActivate(hwnd)
}

; "In front" = you can see it: it's active, one of its menus/dialogs is active,
; it's pinned on top, or nothing is covering the middle of it.
InFront(hwnd)
{
    if WinGetMinMax(hwnd) = -1
        return false
    fg := WinExist("A")
    if fg = hwnd
        return true
    try
        if fg && WinGetPID(fg) = WinGetPID(hwnd)
            return true
    if WinGetExStyle(hwnd) & 0x8          ; pinned (topmost)
        return true
    WinGetPos(&x, &y, &w, &h, hwnd)
    for pt in [[x + w // 2, y + h // 2], [x + w // 2, y + 20], [x + w // 2, y + h - 20]]
    {
        under := DllCall("WindowFromPoint", "Int64", (pt[2] << 32) | (pt[1] & 0xFFFFFFFF), "Ptr")
        if under && DllCall("GetAncestor", "Ptr", under, "UInt", 2, "Ptr") = hwnd
            return true
    }
    return false
}
