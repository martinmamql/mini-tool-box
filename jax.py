# print
jax.debug.print("{}", value)

# create random array
from jax import random
a = random.normal(random.PRNGKey(1), shape=(5, 5))
