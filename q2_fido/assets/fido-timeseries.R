library(fido)
library(dplyr)
library(driver)
library(ggplot2)
library(feather)

args <- commandArgs(TRUE)
biom.name <- args[[1]]
map.name <- args[[2]]
time.column <- args[[3]]
mc.samples <- args[[4]]
output <- args[[5]]


table <-read.csv(biom.name, check.names=FALSE, row.names=1)
map <- read.csv(map.name, check.names=FALSE, row.names=1)
D <- dim(table)[2]

# Specify Priors
Gamma <- function(X){
  distT <- dist(t(X[3,])) %>% as.matrix()  # time
  sigma <- 1
  rho <- 10
  jitter <- 1e-1
  N = ncol(X)
  distTot <- sigma ^ 2 * exp((distT)^2 / rho ^ 2 + jitter * diag(N))
  return(distTot)
}
X <- t(map)
X <- as.data.frame.matrix(X)
Y <- t(as.matrix(table))
N = dim(X)[2]
Theta <- function(X) matrix(0, D-1, ncol(X))
upsilon <- D - 1 + 3
Xi <- matrix(.4, D - 1, D - 1)
diag(Xi) <- 1

# Now fit the model
fit <- fido::basset(Y, X, upsilon, Theta, Gamma, Xi)


write_feather(fit$Lambda, output)
