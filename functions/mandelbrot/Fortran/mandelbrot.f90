MODULE mandelbrot

   IMPLICIT NONE

   PRIVATE

   PUBLIC :: sample_area

CONTAINS

   FUNCTION sample_area(real_start, real_end, imag_start, imag_end, max_iters, width, height, smooth) RESULT(set)

      REAL, INTENT(IN) :: real_start, real_end, imag_start, imag_end
      INTEGER, INTENT(IN) :: max_iters
      INTEGER, INTENT(IN) :: width, height
      LOGICAL, INTENT(IN) :: smooth
      REAL, DIMENSION(width, height) :: set
      INTEGER :: ix, iy, i
      REAL :: x, y
      COMPLEX :: z, c

      set = 0.
      DO iy = 1, height
         DO ix = 1, width
            x = real_start + (real_end - real_start)*(ix - 1)/(width - 1)
            y = imag_end + (imag_start - imag_end)*(iy - 1)/(height - 1)
            z = cmplx(0., 0.)
            c = cmplx(x, y)
            DO i = 1, max_iters
               z = z**2 + c
               IF (abs(z) > 2.) THEN
                  IF (smooth) THEN
                     set(ix, iy) = real(i) + 1.-log(log(abs(z)))/log(2.)
                  ELSE
                     set(ix, iy) = real(i)
                  END IF
                  EXIT
               END IF
            END DO
         END DO
      END DO

   END FUNCTION sample_area

END MODULE mandelbrot
