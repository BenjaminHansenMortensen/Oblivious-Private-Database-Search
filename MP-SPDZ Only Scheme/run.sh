#!/bin/bash

cd ../../MP-SPDZ/

./atlas-party.x MP-SPDZ_Only_Scheme -p 0 -N 3 -IF ../PycharmProjects/MasterThesis/Client/MP-SPDZ\ Inputs/MP-SPDZ_Only_Input -OF ../PycharmProjects/MasterThesis/Client/MP-SPDZ\ Outputs/MP-SPDZ_Only_Output &
./atlas-party.x MP-SPDZ_Only_Scheme -p 1 -N 3 -IF ../PycharmProjects/MasterThesis/Server/MP-SPDZ\ Inputs/MP-SPDZ_Only_Input &
./atlas-party.x MP-SPDZ_Only_Scheme -p 2 -N 3
