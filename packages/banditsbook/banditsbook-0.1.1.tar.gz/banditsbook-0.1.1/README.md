# Bandit Code for the Book "Reinforcement Learning"

This repository was forked from [John Myles White's "BanditsBook" repository](https://github.com/johnmyleswhite/BanditsBook).

I have removed all the non-python code and added a setup.py file to allow for pip installs. Everything else is the same.

## Installing

```
pip install banditsbook
```

## Getting Started

```
from arms.bernoulli import BernoulliArm
from testing_framework.tests import test_algorithm
from algorithms.epsilon_greedy.standard import EpsilonGreedy
num_sims = 1000
horizon = 10

arm0 = BernoulliArm(0.2)
arm1 = BernoulliArm(0.2)
arms = [arm0, arm1]
algo1 = EpsilonGreedy(0.1, [], [])
sim_nums, times, chosen_arms, rewards, cumulative_rewards = test_algorithm(
    algo1, arms, num_sims, horizon)
print(rewards)
```

See the original repository for more information: https://github.com/johnmyleswhite/BanditsBook

Icons made by <a href="https://www.flaticon.com/authors/good-ware" title="Good Ware">Good Ware</a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>