# ![Open Quantum Design](https://raw.githubusercontent.com/OpenQuantumDesign/oqd-compiler-infrastructure/main/docs/img/oqd-logo-text.png)

<h2 align="center">
    Open Quantum Design: Compiler Infrastructure
</h2>

[![doc](https://img.shields.io/badge/documentation-lightblue)](https://docs.openquantumdesign.org/open-quantum-design-compiler-infrastructure)
[![PyPI Version](https://img.shields.io/pypi/v/oqd-compiler-infrastructure)](https://pypi.org/project/oqd-compiler-infrastructure)
[![CI](https://github.com/OpenQuantumDesign/oqd-compiler-infrastructure/actions/workflows/pytest.yml/badge.svg)](https://github.com/OpenQuantumDesign/oqd-compiler-infrastructure/actions/workflows/pytest.yml)
![versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-brightgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)



### What's here:
This repository contains the supporting infrastructure, base classes, and abstractions 
for creating custom compiler analysis, verification, and transformation passes.
The modules in the repository are utilized for, e.g., lowering from the analog to atomic
intermediate representations, and the atomic representation to bare metal descriptions of
quantum programs.

## Installation

Install with `pip`:
```bash
pip install oqd-compiler-infrastructure
```

or alternatively from `git`:
```bash
pip install git+https://github.com/OpenQuantumDesign/oqd-compiler-infrastructure.git
```

For development, clone the repository locally:

```bash
git clone https://github.com/OpenQuantumDesign/oqd-compiler-infrastructure.git
```

## Documentation

To deploy the documentation locally, implemented with [mkdocs](https://www.mkdocs.org/), run the following commands:

```bash
pip install .[docs]
mkdocs serve
```

```mermaid
block-beta
   columns 3
   
   block:Interface
       columns 1
       InterfaceTitle("<i><b>Interfaces</b><i/>")
       InterfaceDigital["<b>Digital Interface</b>\nQuantum circuits with discrete gates"] 
       space
       InterfaceAnalog["<b>Analog Interface</b>\n Continuous-time evolution with Hamiltonians"] 
       space
       InterfaceAtomic["<b>Atomic Interface</b>\nLight-matter interactions between lasers and ions"]
       space
    end
    
    block:IR
       columns 1
       IRTitle("<i><b>IRs</b><i/>")
       IRDigital["Quantum circuit IR\nopenQASM, LLVM+QIR"] 
       space
       IRAnalog["openQSIM"]
       space
       IRAtomic["openAPL"]
       space
    end
    
    block:Emulator
       columns 1
       EmulatorsTitle("<i><b>Classical Emulators</b><i/>")
       
       EmulatorDigital["Pennylane, Qiskit"] 
       space
       EmulatorAnalog["QuTiP, QuantumOptics.jl"]
       space
       EmulatorAtomic["TrICal, QuantumIon.jl"]
       space
    end
    
    space
    block:RealTime
       columns 1
       RealTimeTitle("<i><b>Real-Time</b><i/>")
       space
       RTSoftware["ARTIQ, DAX, OQDAX"] 
       space
       RTGateware["Sinara Real-Time Control"]
       space
       RTHardware["Lasers, Modulators, Photodetection, Ion Trap"]
       space
       RTApparatus["Trapped-Ion QPU (<sup>171</sup>Yt<sup>+</sup>, <sup>133</sup>Ba<sup>+</sup>)"]
       space
    end
    space
    
   InterfaceDigital --> IRDigital
   InterfaceAnalog --> IRAnalog
   InterfaceAtomic --> IRAtomic
   
   IRDigital --> IRAnalog
   IRAnalog --> IRAtomic
   
   IRDigital --> EmulatorDigital
   IRAnalog --> EmulatorAnalog
   IRAtomic --> EmulatorAtomic
   
   IRAtomic --> RealTimeTitle
   
   RTSoftware --> RTGateware
   RTGateware --> RTHardware
   RTHardware --> RTApparatus
   
    classDef title fill:#d6d4d4,stroke:#333,color:#333;
    classDef digital fill:#E7E08B,stroke:#333,color:#333;
    classDef analog fill:#E4E9B2,stroke:#333,color:#333;
    classDef atomic fill:#D2E4C4,stroke:#333,color:#333;
    classDef realtime fill:#B5CBB7,stroke:#333,color:#333;

    classDef highlight fill:#f2bbbb,stroke:#333,color:#333,stroke-dasharray: 5 5;
    
    class InterfaceTitle,IRTitle,EmulatorsTitle,RealTimeTitle title
    class InterfaceDigital,IRDigital,EmulatorDigital digital
    class InterfaceAnalog,IRAnalog,EmulatorAnalog analog
    class InterfaceAtomic,IRAtomic,EmulatorAtomic atomic
    class RTSoftware,RTGateware,RTHardware,RTApparatus realtime
   
```
The lowering and compilation passes, used in the vertical lines connecting
abstraction layers, are based on the compiler infrastructure components contained 
in this repository.