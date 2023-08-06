
program prog_ex1

implicit none


!> Usage:
!
!pyccel test.py -t
!gfortran test.f90 -lblas
!./a.out


!TODO add saxpy test







call test_daxpy()
contains

!........................................
subroutine test_daxpy() 

  implicit none
  integer(kind=4) :: n  
  real(kind=8) :: sa  
  integer(kind=4) :: incx  
  real(kind=8), allocatable :: sx (:) 
  integer(kind=4) :: incy  
  real(kind=8), allocatable :: sy (:) 

  n = 5
  sa = 1.0d0


  incx = 1
  allocate(sx(0:n - 1))
  sx = 0.0


  incy = 1
  allocate(sy(0:n - 1))
  sy = 0.0


  sx(0) = 1.0d0
  sx(1) = 3.0d0
  sx(3) = 5.0d0


  sy(0) = 2.0d0
  sy(1) = 4.0d0
  sy(3) = 6.0d0


  call daxpy(n, sa, sx, incx, sy, incy)
end subroutine
!........................................

end program prog_ex1