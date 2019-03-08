/*
 * Copyright © 2019-present Lenovo
 * 
 * This file is licensed under both the BSD-3 license for individual/non-commercial use and
 * EPL-1.0 license for commercial use. Full text of both licenses can be found in
 * COPYING.BSD and COPYING.EPL files.
 */

const optimizers = [
  {
    'key': 'adadelta',
    'label': 'JobTemplate.Optimizer.Adadelta',
    'params': [
      {
        'key': 'decayRate',
        'label': 'JobTemplate.Optimizer.Adadelta.DecayRate',
        'type': 'number'
      }
    ]
  },
  {
    'key': 'adagrad',
    'label': 'JobTemplate.Optimizer.Adagrad',
    'params': [
      {
        'key': 'initAccumulator',
        'label': 'JobTemplate.Optimizer.Adagrad.InitAccumulator',
        'type': 'number'
      }
    ]
  },
  {
    'key': 'adam',
    'label': 'JobTemplate.Optimizer.Adam',
    'params': [
      {
        'key': 'beta1',
        'label': 'JobTemplate.Optimizer.Adam.Beta1',
        'type': 'number'
      },
      {
        'key': 'beta2',
        'label': 'JobTemplate.Optimizer.Adam.Beta2',
        'type': 'number'
      },
      {
        'key': 'epsilon',
        'label': 'JobTemplate.Optimizer.Adam.Epsilon',
        'type': 'number'
      }
    ]
  },
  {
    'key': 'ftrl',
    'label': 'JobTemplate.Optimizer.FTRL',
    'params': [
      {
        'key': 'learningRatePower',
        'label': 'JobTemplate.Optimizer.FTRL.LearningRatePower',
        'type': 'number'
      },
      {
        'key': 'initAccumulator',
        'label': 'JobTemplate.Optimizer.FTRL.InitAccumulator',
        'type': 'number'
      },
      {
        'key': 'l1',
        'label': 'JobTemplate.Optimizer.FTRL.L1',
        'type': 'number'
      },
      {
        'key': 'l2',
        'label': 'JobTemplate.Optimizer.FTRL.L2',
        'type': 'number'
      }
    ]
  },
  {
    'key': 'momentum',
    'label': 'JobTemplate.Optimizer.Momentum',
    'params': [
      {
        'key': 'momentum',
        'label': 'JobTemplate.Optimizer.Momentum.Momentum',
        'type': 'number'
      }
    ]
  },
  {
    'key': 'sgd',
    'label': 'JobTemplate.Optimizer.SGD',
    'params': [
      {
        'key': 'gradientNorm',
        'label': 'JobTemplate.Optimizer.SGD.GradientNorm',
        'type': 'number'
      },
      {
        'key': 'maxGradientNorm',
        'label': 'JobTemplate.Optimizer.SGD.MaxGradientNorm',
        'type': 'number'
      },
      {
        'key': 'gradientNormGlobalFirst',
        'label': 'JobTemplate.Optimizer.SGD.GradientNormGlobalFirst',
        'type': 'bool'
      }
    ]
  },
  {
    'key': 'rmsprop',
    'label': 'JobTemplate.Optimizer.RMSProp',
    'params': [
      {
        'key': 'momentum',
        'label': 'JobTemplate.Optimizer.RMSProp.Momentum',
        'type': 'number'
      },
      {
        'key': 'decayRate',
        'label': 'JobTemplate.Optimizer.RMSProp.DecayRate',
        'type': 'number'
      }
    ]
  }
];

export default {
  optimizers
}
