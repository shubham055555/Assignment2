; ============================================================
; x86-64 NASM — String Reversal
; ENCS302 Assignment 2
; Build:  nasm -f elf64 strrev_x86.asm -o strrev_x86.o
;         ld strrev_x86.o -o strrev_x86
; Reverses "HELLO" → "OLLEH"
; ============================================================

section .data
    src     db  "HELLO", 0
    msg1    db  "Original : HELLO", 10, 0
    msg2    db  "Reversed : ", 0
    newline db  10, 0

section .bss
    buf     resb 16

section .text
    global _start

_start:
    ; Print original
    mov     rdi, msg1
    call    print_str

    ; Find string length
    mov     rsi, src
    mov     rcx, 0
.len_loop:
    cmp     byte [rsi + rcx], 0
    jz      .len_done
    inc     rcx
    jmp     .len_loop
.len_done:
    ; rcx = length

    ; Reverse: two-pointer swap
    mov     rdi, buf
    mov     rsi, src
    ; Copy src to buf first
    mov     rdx, 0
.copy:
    mov     al, [rsi + rdx]
    mov     [rdi + rdx], al
    inc     rdx
    cmp     rdx, rcx
    jl      .copy
    mov     byte [rdi + rcx], 0    ; null terminate

    ; In-place reverse buf
    xor     rax, rax            ; left  = 0
    mov     rbx, rcx
    dec     rbx                 ; right = len-1
.rev_loop:
    cmp     rax, rbx
    jge     .rev_done
    mov     cl, [buf + rax]
    mov     dl, [buf + rbx]
    mov     [buf + rax], dl
    mov     [buf + rbx], cl
    inc     rax
    dec     rbx
    jmp     .rev_loop
.rev_done:

    ; Print reversed
    mov     rdi, msg2
    call    print_str
    mov     rdi, buf
    call    print_str
    mov     rdi, newline
    call    print_str

    mov     rax, 60
    xor     rdi, rdi
    syscall

; ── print_str(rdi=ptr) ───────────────────────────────────
print_str:
    push    rdi
    mov     rsi, rdi
    mov     rdx, 0
.len:
    cmp     byte [rsi + rdx], 0
    jz      .write
    inc     rdx
    jmp     .len
.write:
    mov     rax, 1
    mov     rdi, 1
    syscall
    pop     rdi
    ret
