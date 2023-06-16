#!/bin/bash

for entry in *
do
  pngcrush -ow -rem allb -reduce $entry
done