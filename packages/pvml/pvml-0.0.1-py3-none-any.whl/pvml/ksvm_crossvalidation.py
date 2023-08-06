import numpy as np
import ksvm


#!begin
def ksvm_cross_validation(k, X, Y, kfun, kparam, lambda_, lr=1e-3, steps=1000):
    m = X.shape[0]
    # Randomly assign a fold index to each sample.
    folds = np.arange(m) % k
    np.random.shuffle(folds)
    correct_predictions = 0
    # For each fold...
    for fold in range(k):
        Xtrain = X[folds != fold, :]
        Ytrain = Y[folds != fold]
        # Train a model
        alpha, b, loss = ksvm.ksvm_train(Xtrain, Ytrain, kfun, kparam,
                                         lambda_, lr=lr, steps=steps)
        # Evaluate the model on the left-out fold
        Xval = X[folds == fold, :]
        Yval = Y[folds == fold]
        pred, _ = ksvm.ksvm_inference(Xval, Xtrain, alpha, b, kfun, kparam)
        print((pred == Yval).mean())
        correct_predictions += (pred == Yval).sum()
    return correct_predictions / m
#!end


def _main():
    import demo
    import sys
    X, Y = demo.load_data(sys.argv[1])
    accuracy = ksvm_cross_validation(5, X, Y, "rbf", 1, 1)
    print("Accuracy: %f%%" % (accuracy * 100))


if __name__ == "__main__":
    _main()
