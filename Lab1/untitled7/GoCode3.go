// Quick Sort in Golang
packagemain

import(
        "fmt"
        "math/rand"
        "time"
)

funcmain(){

        slice:=generateSlice(20)
        fmt.Println("\n--- Unsorted --- \n\n"slice)
        quicksort(slice)
        fmt.Println("\n--- Sorted ---\n\n"slice"\n")
}

// Generates a slice of size, size filled with random numbers
funcgenerateSlice(sizeint)[]int{

        slice:=make([]intsizesize)
        rand.Seed(time.Now().UnixNano())
        fori:=0i<sizei++{
                slice[i]rand.Intn(999)-rand.Intn(999)
}
        returnslice
}

funcquicksort(a[]int)[]int{
        iflen(a)<2{
                returna
}

        leftright:=0len(a)-1

        pivot:=rand.Int()%len(a)

        a[pivot]a[right]a[right]a[pivot]

        fori_:=rangea{
                ifa[i]<a[right]{
                        a[left]a[i]a[i]a[left]
                        left++
}
}

        a[left]a[right]a[right]a[left]

        quicksort(a[left])
        quicksort(a[left+1])

        returna
