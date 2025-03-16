readMatrix <- function(datam, nrows, cname, lower=1)
{ 
        # data.m <- scan(datam)
        # lower=1 : Lower  Triangular Matrix (default)
        # lower=2 : upper  Triangular Matrix 
        n <- nrows

        if( lower == 1)
        {  DistanceArray <- array(0, n*(n-1)/2 )
           for(i in 1:(n-1) )
             for(j in (i+1):n )
                 { kk1 <- (j-1)*(j-2)/2 + i
                   kk2 <- n*(i-1)- i*(i-1)/2 + j-i
                   DistanceArray[kk2] <- datam[kk1] }
        }
        else
             DistanceArray <- datam
 
     
     DistanceArray = 10 - DistanceArray


     MD <- matrix(0, nrow=n, ncol=n)

     for(j in 1:(n-1) )
        for(k in (j+1):n)
        {    kk <- n*(j-1) - j*(j-1)/2 + k-j
             MD[j,k] <- MD[k,j] <- DistanceArray[kk]
        }
     
     colnames(MD) = cname
     rownames(MD) = cname

     return(MD)
}






