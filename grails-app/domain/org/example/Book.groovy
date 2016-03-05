package org.example

class Book {
    String title
    String author
    static constraints = {
        title(blank:true)
        author(blank:true)
    }
}
