; ============================================================
; x86-64 NASM — Factorial (Iterative Loop)
; ENCS302 Assignment 2
; Build:  nasm -f elf64 factorial_x86.asm -o factorial_x86.o
;         ld factorial_x86.o -o factorial_x86
; Computes 8! = 40320
; ============================================================

section .data
    msg     db  "8! = ", 0
    newline db  10, 0
    result  times 12 db 0

section .text
    global _start

_start:
    mov     rdi, msg
    call    print_str

    ; Compute 8!
    mov     rax, 1              ; result = 1
    mov     rcx, 8              ; counter n = 8
.fact_loop:
    cmp     rcx, 1
    jle     .fact_done
    imul    rax, rcx            ; result *= n
    dec     rcx
    jmp     .fact_loop
.fact_done:
    ; rax = 40320

    mov     rdi, rax
    mov     rsi, result
    call    itoa
    mov     rdi, result
    call    print_str
    mov     rdi, newline
    call    print_str

    mov     rax, 60
    xor     rdi, rdi
    syscall

; ── itoa(rdi=value, rsi=buf) ─────────────────────────────
itoa:
    push    rbx
    push    rcx
    push    r8
    mov     rax, rdi
    mov     rcx, 10
    lea     r8, [rsi + 11]
    mov     byte [r8], 0
    dec     r8
.digit:
    xor     rdx, rdx
    div     rcx
    add     dl, '0'
    mov     [r8], dl
    dec     r8
    test    rax, rax
    jnz     .digit
    inc     r8
    mov     rcx, 0
.copy:
    mov     al, [r8 + rcx]
    mov     [rsi + rcx], al
    test    al, al
    jz      .done
    inc     rcx
    jmp     .copy
.done:
    pop     r8
    pop     rcx
    pop     rbx
    ret

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
