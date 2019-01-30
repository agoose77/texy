# TeXy
Simple python LaTeX generator

`pip install git+https://github.com/agoose77/texy.git#egg=texy`

```python
from texy import latex, _

with latex() as t:
    t("Some text")
    with t.figure['h!']:
        t.includegraphics[_(width=r'\textwidth')]('some_fig.png')
        t.caption('Some Caption')
```

Outputs
```

Some text
\begin{figure}[h!]
    \includegraphics[width=\textwidth]{some_fig.png}
    \caption{Some Caption}
\end{figure}

```
