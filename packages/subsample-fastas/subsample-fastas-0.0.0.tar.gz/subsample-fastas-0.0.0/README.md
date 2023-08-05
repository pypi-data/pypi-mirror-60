# Overview

Randomly alter fasta files by substracting a given % of genes in a genome (fasta) or in a (% of a) set of genomes

  - Free software: CeCILL 2.1 Free Software License

## Installation

    pip install subsample-fastas

## Documentation


To use the project:

``` python
import subsample_fastas
subsample_fastas.longest()
```



## Development

To run the all tests run:

    tox

Note, to combine the coverage data from all the tox environments run:

<table>
<colgroup>
<col style="width: 10%" />
<col style="width: 90%" />
</colgroup>
<tbody>
<tr class="odd">
<td>Windows</td>
<td><pre><code>set PYTEST_ADDOPTS=--cov-append
tox</code></pre></td>
</tr>
<tr class="even">
<td>Other</td>
<td><pre><code>PYTEST_ADDOPTS=--cov-append tox</code></pre></td>
</tr>
</tbody>
</table>
