#!/usr/bin/env Rscript
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


table <-read.table(biom.name, check.names=FALSE, row.names=1)
map <- read.csv(map.name, sep='\t', row.names=1)
D <- dim(table)[2]
N <- dim(table)[1]

# Specify Priors
Gamma <- function(X) SE(X, sigma=5, rho=10) # Create partial function

X <- t(map)
X <- as.data.frame.matrix(X)
Y <- t(as.matrix(table))

Theta <- function(X) matrix(0, D-1, ncol(X))
upsilon <- D - 1 + 3
Xi <- matrix(.4, D - 1, D - 1)
diag(Xi) <- 1

# Now fit the model
fit <- fido::basset(Y, X, upsilon, Theta, Gamma, Xi)

write_feather(fit$Lambda, output)
