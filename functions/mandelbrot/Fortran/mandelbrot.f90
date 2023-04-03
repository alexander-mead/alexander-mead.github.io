MODULE mandelbrot

   IMPLICIT NONE

   INTEGER, PARAMETER :: sp = kind(1.0)
   INTEGER, PARAMETER :: dp = kind(1.0d0)

   PRIVATE

   PUBLIC :: sample_area

CONTAINS

   FUNCTION sample_area(real_start, real_end, imag_start, imag_end, max_iters, width, height) RESULT(set)

      REAL, INTENT(IN) :: real_start, real_end, imag_start, imag_end
      INTEGER, INTENT(IN) :: max_iters
      INTEGER, INTENT(IN) :: width, height
      INTEGER, DIMENSION(width, height) :: set
      INTEGER :: ix, iy, i
      REAL :: x, y
      COMPLEX :: z, c

      set = 0
      DO iy = 1, height
         DO ix = 1, width
            x = real_start + (real_end - real_start)*(ix - 1)/(width - 1)
            y = imag_end + (imag_start - imag_end)*(iy - 1)/(height - 1)
            z = cmplx(0.d0, 0.d0)
            c = cmplx(x, y)
            DO i = 1, max_iters
               z = z**2 + c
               IF (abs(z) > 2.d0) THEN
                  set(ix, iy) = i
                  EXIT
               END IF
            END DO
         END DO
      END DO

   END FUNCTION sample_area

   ! SUBROUTINE sample_area(real_start, real_end, imag_start, imag_end, max_iters, width, height, set)

   !    REAL, INTENT(IN) :: real_start, real_end, imag_start, imag_end
   !    INTEGER, INTENT(IN) :: max_iters
   !    INTEGER, INTENT(IN) :: width, height
   !    !INTEGER, DIMENSION(width, height), INTENT(OUT) :: set
   !    INTEGER, ALLOCATABLE :: set(:, :)
   !    INTEGER :: ix, iy, i
   !    REAL :: x, y
   !    COMPLEX :: z, c

   !    ALLOCATE (set(width, height))
   !    set = 0
   !    DO iy = 1, height
   !       DO ix = 1, width
   !          x = real_start + (real_end - real_start)*(ix - 1)/(width - 1)
   !          y = imag_end + (imag_start - imag_end)*(iy - 1)/(height - 1)
   !          z = cmplx(0.d0, 0.d0)
   !          c = cmplx(x, y)
   !          DO i = 1, max_iters
   !             z = z**2 + c
   !             IF (abs(z) > 2.d0) THEN
   !                set(ix, iy) = i
   !                EXIT
   !             END IF
   !          END DO
   !       END DO
   !    END DO

   ! END SUBROUTINE sample_area

END MODULE mandelbrot
