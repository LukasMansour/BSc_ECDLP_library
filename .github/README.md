# (EC)DLP Arithmetics for Qiskit

This small library was part of my Bachelor's examination. 
I used it to create quantum arithmetic circuits for resource estimates.
It includes many important quantum arithmetic circuits allowing one to
run Shor's algorithm with a semi-classical quantum fourier transform to DLP instances.

It works for the multiplicative integer group and elliptic curve groups.

## Table of Contents

- [Open improvements](#open-improvements-and-ideas)
- [Maintainers](#maintainers)
- [License](#license)

## Open Improvements and Ideas

There are quite a few open improvements still available, I will try to shortly explain each one.
If anyone would like more information, feel free to contact me.

### Layouts of dirty qubits

When we borrow a qubit (use dirty qubits) we typically have a choice between a set of qubits.
Can we choose those qubits so that the layout is better?
This becomes especially important for resource estimates on actual quantum hardware.

At the moment, we just choose them by order of insertion to the circuit.

### Pebbeling

Pebbeling in quantum circuits, involves improving a circuit by combining operations.
As an example, in elliptic curve addition, we could instead of calculating _x*y_, then adding the result to a register _p_ and then reversing _x*y_,
we could get _x*y_, taint a few ancillas (do not uncompute!), add to _p_ and immediately reverse the computation from _x*y_, untainting the ancillas.
This would save the gate operations that are done to uncompute ancillas all throughout the elliptic-curve addition circuit.
In principle this can be applied to a variety of different circuits.

### Better overall circuit structures

Of course the largest way to improve these circuits, would be to find new discoveries
and improvements to underlying components, finding a linear time incrementer with a low
constant factor would be a huge improvement. Similarly, finding a modular inversion circuit that does not have an absurdly high scaling would be monumental.

### Circuit Baking / Currying

Circuit baking would be another way to develop interesting quantum-classical
circuits, unfortunately there is no easy way to do circuit baking with qiskit.
Perhaps something like this is doable in RevKit or other libraries for reversible computing.

Circuit baking involves taking a quantum-quantum adder and fixing the input, as an
example I could take the TTK Adder, fix one input to be _|001>_ (to get e.g. an incrementer) and then remove gates
that will never trigger.

### Other representations of modular arithmetic

There are other representations of modular arithmetic, that can have
advantages for circuits, the two most prominent are **Montgomery Reduction** and **Barret Reduction**.

There do exist some circuits for these representations, however, out of time-constraints
I decided against implementing them. Also, for overall arithmetic they do not change much.

### Completely different integer representation

Another idea would be to completely change the representation entirely (or to switch representation) throughout the circuit.
As an example, we could use Zeckendorf-representation or any sequence-based representation.

It may be that a different representation makes certain operations easier. (See [here](https://r-knott.surrey.ac.uk/Fibonacci/fibrep.html#section6.2) for more information)

### Quantum GCD

I skipped over calculating the GCD (Greatest-Common-Denominator) with a quantum circuit efficentely.
I achieved this by using a circuit based on Fermat's Little Theorem,
though it is inefficient to construct (exponential time), it can be run on today's simulators.

The Quantum GCD requires many qubits to store intermediate results and is not feasibly
simulatable with Shor's algorithm yet. It can be simulated efficiently as it is a fully reversible classical arithmetic circuit.
However, it cannot be simulated with superpositions, due to the high qubit count and exponential size of the Hilbert space.
These are of course required for the phase-kickback to actually take place and Shor's algorithm to deliver actual results.

### Improvements to CDKM Structures
There are a variety of improvements for CDKM structures (different majority-add and unmajority-add circuits).
More information [here](https://arxiv.org/pdf/1612.07424)

### Adding QFT Arithmetic

In principle it would be very easy to add QFT arithmetic, allowing for hybrid circuits (both Fourier and binary encoding).
The Qiskit optimiser would remove any symmetric QFT cases and so, by adding QFT arithmetic and ensuring the encoding after
applying iQFT is consistent with binary encoding, one could further improve the circuit library.

### Adding Windowed Arithmetic

There are also a variety of papers regarding windowed quantum arithmetic, that could be used to reduce the complexity of certain operations.

### Comparative Metrics

It would be even more interesting to introduce comparative metrics, which would allow one to nest metrics, e.g.
optimise by gate count and then if equal optimise by depth.

### More Copy-Control Circuits

We only implemented a copy-control circuit for quantum-classical non-modular addition. 
There is still an opportunity to add it for quantum-classical modular addition and quantum-classical modular multiplication.

### Adding a Build System

There should probably be a build system in-place to automagically run tests using a CI environment.
## Maintainers

[@Lukas Mansour](https://github.com/LukasMansour)

## Special Thanks
- Reference Implementation from Microsoft: (https://github.com/microsoft/QuantumEllipticCurves)
- Reference Implementation by Mandl and Egly: (https://github.com/mhinkie/ShorDiscreteLog)
- Quaspy Library by Martin Ekerå: (https://github.com/ekera/quaspy)
- Circuit explanations and snippets by Egretta Thula {I highly recommend you read their blog!}: (https://egrettathula.wordpress.com/category/circuit-construction/page/2/)
- Craig Gidney for his blog: (https://algassert.com/)
- The Quantum Computing Stack Exchange Community: (https://quantumcomputing.stackexchange.com/)

## License

I have decided to not actively license this work, as it is based on the developments and
improvements of many different scientists, doing so would be an infringement on their contributions. I have no claim to their ideas or advancements. This software was purely created for a Bachelor's degree and to test the functionality of quantum arithmetic circuits.
Some code snippets have been adapted from their original authors, but in such a case, should contain a reference to the original author.

Hence, in the name of free and open science, this library is basically public domain. You could just as well download the papers from arxiv and implement
this entire library your self, which I welcome you to do and will teach you a lot about quantum arithmetic!

Should you ever want to extend on the work, I ask of you to open a pull-request
and include it here, or at least let me know!

Of course, there is no warranty for this software and the authors or maintainers cannot be held liable for any damages.