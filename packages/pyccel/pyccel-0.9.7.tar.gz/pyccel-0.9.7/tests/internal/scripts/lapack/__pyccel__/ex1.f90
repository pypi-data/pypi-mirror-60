
program prog_ex1

implicit none


!> Usage:
!
!pyccel test.py -t
!gfortran test.f90 -lblas -llapack
!./a.out


!TODO: - assert






















!assert(info == 0)

!assert(info == 0)

!assert(info == 0)

!assert(info == 0)
call test_1()
call test_2()
call test_3()
call test_4()
contains

!........................................
subroutine test_1() 

  implicit none
  integer(kind=4) :: n  
  integer(kind=4) :: ml  
  integer(kind=4) :: mu  
  integer(kind=4) :: lda  
  real(kind=8), allocatable :: a (:,:) 
  real(kind=8), allocatable :: b (:) 
  integer(kind=4) :: m  
  integer(kind=4) :: info  
  integer(kind=4), allocatable :: ipiv (:) 

  n = 25
  ml = 1
  mu = 1
  lda = 2*ml + mu + 1


  allocate(a(0:n - 1, 0:lda - 1))
  a = 0.0
  allocate(b(0:n - 1))
  b = 0.0


  b(0) = 1.0d0
  b(n - 1) = 1.0d0


  !Superdiagonal, Diagonal, Subdiagonal
  m = ml + mu
  a(1:n - 1, m - 1) = -1.0d0
  a(0:n - 1, m) = 2.0d0
  a(0:n - 2, m + 1) = -1.0d0


  info = -1
  allocate(ipiv(0:n - 1))
  ipiv = 0


  call dgbtrf(n, n, ml, mu, a, lda, ipiv, info)
  !assert(info == 0)


  call dgbtrs('n', n, ml, mu, 1, a, lda, ipiv, b, n, info)
end subroutine
!........................................

!........................................
subroutine test_2() 

  implicit none
  integer(kind=4) :: n  
  integer(kind=4) :: lda  
  real(kind=8), allocatable :: a (:,:) 
  integer(kind=4) :: info  
  integer(kind=4), allocatable :: ipiv (:) 
  integer(kind=4), allocatable :: iwork (:) 
  integer(kind=4) :: lwork  
  real(kind=8), allocatable :: work (:) 
  real(kind=8) :: anorm  
  real(kind=8) :: rcond  

  n = 3
  lda = n


  allocate(a(0:n - 1, 0:lda - 1))
  a = 0.0


  a(0, 0) = 0.0d0
  a(1, 0) = 1.0d0
  a(2, 0) = 2.0d0


  a(0, 1) = 4.0d0
  a(1, 1) = 5.0d0
  a(2, 1) = 6.0d0


  a(0, 2) = 7.0d0
  a(1, 2) = 8.0d0
  a(2, 2) = 0.0d0


  info = -1
  allocate(ipiv(0:n - 1))
  ipiv = 0


  call dgetrf(n, n, a, lda, ipiv, info)
  !assert(info == 0)


  allocate(iwork(0:n - 1))
  iwork = 0
  lwork = 4*n
  allocate(work(0:lwork - 1))
  work = 0.0


  !Get the condition number.
  anorm = 1.0d0
  rcond = -1.0d0
  call dgecon('I', n, a, lda, anorm, rcond, work, iwork, info)
end subroutine
!........................................

!........................................
subroutine test_3() 

  implicit none
  integer(kind=4) :: n  
  integer(kind=4) :: lda  
  real(kind=8), allocatable :: a (:,:) 
  integer(kind=4) :: info  
  integer(kind=4), allocatable :: ipiv (:) 
  integer(kind=4), allocatable :: iwork (:) 
  integer(kind=4) :: lwork  
  real(kind=8), allocatable :: work (:) 

  n = 3
  lda = n


  allocate(a(0:n - 1, 0:lda - 1))
  a = 0.0


  a(0, 0) = 0.0d0
  a(1, 0) = 1.0d0
  a(2, 0) = 2.0d0


  a(0, 1) = 4.0d0
  a(1, 1) = 5.0d0
  a(2, 1) = 6.0d0


  a(0, 2) = 7.0d0
  a(1, 2) = 8.0d0
  a(2, 2) = 0.0d0


  info = -1
  allocate(ipiv(0:n - 1))
  ipiv = 0


  call dgetrf(n, n, a, lda, ipiv, info)
  !assert(info == 0)


  allocate(iwork(0:n - 1))
  iwork = 0
  lwork = 4*n
  allocate(work(0:lwork - 1))
  work = 0.0


  !Compute the inverse matrix.
  call dgetri(n, a, lda, ipiv, work, lwork, info)
end subroutine
!........................................

!........................................
subroutine test_4() 

  implicit none
  integer(kind=4) :: n  
  integer(kind=4) :: lda  
  real(kind=8), allocatable :: a (:,:) 
  integer(kind=4) :: info  
  integer(kind=4), allocatable :: ipiv (:) 
  real(kind=8), allocatable :: b (:) 

  n = 3
  lda = n


  allocate(a(0:n - 1, 0:lda - 1))
  a = 0.0


  a(0, 0) = 0.0d0
  a(1, 0) = 1.0d0
  a(2, 0) = 2.0d0


  a(0, 1) = 4.0d0
  a(1, 1) = 5.0d0
  a(2, 1) = 6.0d0


  a(0, 2) = 7.0d0
  a(1, 2) = 8.0d0
  a(2, 2) = 0.0d0


  info = -1
  allocate(ipiv(0:n - 1))
  ipiv = 0


  call dgetrf(n, n, a, lda, ipiv, info)
  !assert(info == 0)


  !Compute the inverse matrix.
  allocate(b(0:n - 1))
  b = 0.0
  b(0) = 14.0d0
  b(1) = 32.0d0
  b(2) = 23.0d0


  !Solve the linear system.
  call dgetrs('n', n, 1, a, lda, ipiv, b, n, info)
end subroutine
!........................................

end program prog_ex1