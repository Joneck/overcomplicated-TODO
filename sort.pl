countWords([],0).
countWords([_|X],N) :- countWords(X,PrevN), N is PrevN + 1.


checkEachTask([], []).
checkEachTask([X|Xs], [[COUNTER, X]|Final]) :- 
    split_string(X, " ", "", SPLITTED),
    countWords(SPLITTED, COUNTER),
    checkEachTask(Xs, Final).


divide([], [], []).
divide([A], [A], []).
divide([A, B|L], [A|L1], [B|L2]) :- divide(L, L1, L2).


merge([], B, B).
merge(A, [], A).
merge([[A1, A2]|As], [[B1, B2]|Bs], [[A1, A2]|Rest]) :- A1 >= B1, merge(As, [[B1, B2]|Bs], Rest).
merge([[A1, A2]|As], [[B1, B2]|Bs], [[B1, B2]|Rest]) :- A1 < B1, merge([[A1, A2]|As], Bs, Rest).

mergesort([], []).
mergesort([A], [A]).
mergesort(A, Sorted) :- 
    divide(A, Front, Back),
    mergesort(Front, SortedFront),
    mergesort(Back, SortedBack),
    merge(SortedFront, SortedBack, Sorted).