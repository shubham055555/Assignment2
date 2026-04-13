; ============================================================
; x86-64 NASM — GCD (Euclidean Algorithm)
; ENCS302 Assignment 2
; Build:  nasm -f elf64 gcd_x86.asm -o gcd_x86.o
;         ld gcd_x86.o -o gcd_x86
; Computes GCD(48, 18) → 6
; ============================================================

section .data
    msg     db  "GCD(48, 18) = ", 0
    newline db  10, 0
    result  times 12 db 0       ; buffer for itoa

section .text
    global _start

_start:
    ; Print label
    mov     rdi, msg
    call    print_str

    ; Compute GCD(48, 18)
    mov     rax, 48             ; a = 48
    mov     rbx, 18             ; b = 18
    call    gcd                 ; result in rax

    ; Print result
    mov     rdi, rax
    mov     rsi, result
    call    itoa
    mov     rdi, result
    call    print_str

    ; Print newline
    mov     rdi, newline
    call    print_str

    ; Exit
    mov     rax, 60
    xor     rdi, rdi
    syscall

; ── gcd(rax=a, rbx=b) → rax ─────────────────────────────
; while rbx != 0: rdx = rax % rbx; rax = rbx; rbx = rdx
gcd:
    test    rbx, rbx
    jz      .done
.loop:
    xor     rdx, rdx
    div     rbx                 ; rax = rax/rbx, rdx = rax%rbx
    mov     rax, rbx
    mov     rbx, rdx
    test    rbx, rbx
    jnz     .loop
.done:
    ret

; ── itoa(rdi=value, rsi=buf) ─────────────────────────────
; Converts integer in rdi to decimal string at rsi
itoa:
    push    rbx
    push    rcx
    push    r8
    mov     rax, rdi
    mov     rcx, 10
    lea     r8, [rsi + 11]
    mov     byte [r8], 0        ; null terminate
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
    ; shift string to rsi
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
    mov     rax, 1              ; sys_write
    mov     rdi, 1              ; stdout
    syscall
    pop     rdi
    ret
