package org.example

import grails.converters.JSON

class BookController {

    def scaffold = Book
    def list(){
        obj = [
                {
                    name:'muali'
                    file:'1.jpg'
                    filepath:'dest/1.jpg'
                },
                {
                    name:'muali'
                    file:'2.jpg'
                    filepath:'dest/1.jpg'
                },
                {
                    name:'muali'
                    file:'3.jpg'
                    filepath:'dest/3.jpg'
                },
                {
                    name:'muali'
                    file:'4.jpg'
                    filepath:'dest/4.jpg'
                }
        ]
        render obj as JSON

    }

}
