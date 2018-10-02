# texy
Simple python Latex generator

```python
from texy import latex
with latex() as t:
    with t.figure._('h!'):
        t.includegraphics._(width=r'\textwidth')('some_fig.png')
        t.caption('Some Caption')
```

Outputs
```
\begin{figure}[h!]
    \includegraphics[ss, width=\textwidth]{some_fig.png}
    \caption{Some Caption}
\end{figure}
```
