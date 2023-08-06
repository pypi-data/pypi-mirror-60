
program prog_allgather

use mpi
implicit none

integer(kind=4) :: rank  
integer(kind=4) :: comm  
integer(kind=4) :: block_length  
integer(kind=4) :: nb_values  
integer(kind=4) :: size  
integer(kind=4), allocatable :: values (:) 
integer(kind=4), allocatable :: data (:) 
integer(kind=4) :: i  
integer(kind=4) :: ierr  
!coding: utf-8















!we need to declare these variables somehow,
!since we are calling mpi subroutines
ierr = -1
size = -1
rank = -1


call mpi_init(ierr)


comm = mpi_comm_world
call mpi_comm_size(comm, size, ierr)
call mpi_comm_rank(comm, rank, ierr)


nb_values = 8


block_length = floor(nb_values/Real(size, 8))


!...
allocate(values(0:block_length - 1))
values = 0
do i = 0, block_length - 1, 1
  values(i) = i + nb_values*rank + 1000


end do

print *, 'I, process ', rank, 'sent my values array : ', values
!...


!...
allocate(data(0:nb_values - 1))
data = 0


call mpi_allgather(values, block_length, MPI_INTEGER, data, block_length &
      , MPI_INTEGER, comm, ierr)
!...


print *, 'I, process ', rank, ', received ', data


call mpi_finalize(ierr)

end program prog_allgather