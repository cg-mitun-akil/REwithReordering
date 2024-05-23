# REreordering
Runtime enforcement with reordering events

## Basic Codebase Structure
- **benchmarks**: Example input traces
- **output**: Output traces generated for the benchmarks
- **plots**: Plots generated and used in the paper from output traces and src
- **src**: Enforcer algorithm and utility modules to be executed for analysis.

## Running Experiments
1. Place the examples traces in the `benchmarks` folder. (Follow the input format and file naming format)
2. Execute `genOutputTraces.py` to generate the output traces.
3. Execute `sizeVmemPlot.py` to generate plots of size vs Memory for the output traces.
4. Execute `vlinePlot.py` after providing `file_ex_no` in line 77.
5. Execute `genProbvMemTim.py` after providing the file name to generate traces for analyzing probability vs Memory and size.
6. Execute `plotMemory_Prob.py` and `plotTime_Prob.py` after providing the related file name to plot and analyze the output traces generated in step 5.

## Creating a New Input Trace
Each input trace should have the following JSON keys and values:
- **mp**: The automata (each state should be a single character ASCII)
- **alphabets**: Sigma (each alphabet should be a single character ASCII)
- **alpha**: Enforcer configuration of alpha
- **beta**: Enforcer configuration of beta
- **startState**: Starting state
- **acceptedStates**: A list of accepting states
- **events**: A list of tuples of form (event, sequence no) ordered ascendingly w.r.t sequence no.
