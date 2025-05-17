{ lib
, buildPythonPackage
, pythonOlder
, pydantic
, pytest
, pymdown-extensions
, mkdocstrings
, mkdocs-material
, mkdocstrings-python
}:

buildPythonPackage rec {
  pname = "oqd-compiler-infrastructure";
  version = "0.1.0";
  format = "pyproject";

  disabled = pythonOlder "3.10";

  src = ./..;

  propagatedBuildInputs = [
    pydantic
  ];

  checkInputs = [
    pytest
  ];

  nativeBuildInputs = [
    pymdown-extensions
    mkdocstrings
    mkdocs-material
    mkdocstrings-python
  ];

  pythonImportsCheck = [ "oqd_compiler_infrastructure" ];

  meta = with lib; {
    description = "OpenQuantum Design Compiler Infrastructure";
    homepage = "https://github.com/OpenQuantumDesign/oqd-compiler-infrastructure";
    license = licenses.apache20;
    maintainers = with maintainers; [ ];
  };
}
