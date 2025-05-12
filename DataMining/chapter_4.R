####################################
# Ensemble with wine data
####################################

# Importing data
wine = read.csv("c:/data/winequalityCLASS.csv", header=TRUE)

# Factorize for classification
wine$quality = factor(wine$quality)


### Bagging
install.packages("rpart")
install.packages("adabag")
library(rpart)
library(adabag)
set.seed(1234)
my.control = rpart.control(xval=0, cp=0, minsplit=5)
bag.wine = bagging(quality~., data=wine, mfinal=100, control=my.control)
# Variable importance
print(bag.wine$importance)
importanceplot(bag.wine)
# Error vs. number of trees
evol.wine = errorevol(bag.wine, newdata=wine)
plot.errorevol(evol.wine)

# Making predictions
prob.bag.wine = predict.bagging(bag.wine, newdata=wine)$prob
head(prob.bag.wine, 5)
cutoff = 0.5 #cutoff
yhat.bag.wine = ifelse(prob.bag.wine[,2] > cutoff, 1, 0)

# Evaluation
tab = table(wine$quality, yhat.bag.wine, dnn=c("Observed","Predicted"))
print(tab)              # confusion matrix
sum(diag(tab))/sum(tab) # accuracy
tab[2,2]/sum(tab[2,])   # sensitivity
tab[1,1]/sum(tab[1,])   # specificity


### Boosting
library(rpart)
library(adabag)
set.seed(1234)
my.control = rpart.control(xval=0, cp=0, maxdepth=4)
boo.wine = boosting(quality~., data=wine, boos=T, mfinal=100, control=my.control)
# Variable importance
print(boo.wine$importance)
importanceplot(boo.wine)
# Error vs. number of trees
evol.wine = errorevol(boo.wine, newdata=wine)
plot.errorevol(evol.wine)

# Making predictions
prob.boo.wine = predict.boosting(boo.wine, newdata=wine)$prob
head(prob.boo.wine, 5)
cutoff = 0.5 #cutoff
yhat.boo.wine = ifelse(prob.boo.wine[,2] > cutoff, 1, 0)

# Evaluation
tab = table(wine$quality, yhat.boo.wine, dnn=c("Observed","Predicted"))
print(tab)              # confusion matrix
sum(diag(tab))/sum(tab) # accuracy
tab[2,2]/sum(tab[2,])   # sensitivity
tab[1,1]/sum(tab[1,])   # specificity


### Random Forest
install.packages("randomForest")
library(randomForest)
set.seed(1234)
rf.wine = randomForest(quality~., data=wine, ntree=100, mtry=5, 
                       importance=T, na.action=na.omit)
# Variable importance
importance(rf.wine, type=1)
varImpPlot(rf.wine, type=1)
# Plot error rates
plot(rf.wine, type="l")
# Partial dependence plot
partialPlot(rf.wine, pred.data=wine, x.var='alcohol', which.class=1)

# Making predictions
prob.rf.wine = predict(rf.wine, newdata=wine, type="prob") 
head(prob.rf.wine, 5)
cutoff = 0.5 #cutoff
yhat.rf.wine = ifelse(prob.rf.wine[,2] > cutoff, 1, 0)

# Evaluation
tab = table(wine$quality, yhat.rf.wine, dnn=c("Observed","Predicted"))
print(tab)              # confusion matrix
sum(diag(tab))/sum(tab) # accuracy
tab[2,2]/sum(tab[2,])   # sensitivity
tab[1,1]/sum(tab[1,])   # specificity
