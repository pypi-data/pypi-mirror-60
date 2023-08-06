
program prog_ex1

use omp_lib
implicit none

integer(kind=4) :: idx  
integer(kind=4) :: n_threads  
integer(kind=4) :: max_threads  
!coding: utf-8







n_threads = omp_get_num_threads()
print *, "> threads number : ", n_threads


max_threads = omp_get_max_threads()
print *, "> maximum available threads : ", max_threads


!$omp parallel private(idx)


idx = omp_get_thread_num()
print *, "> thread  id : ", idx


!$omp end parallel  

end program prog_ex1