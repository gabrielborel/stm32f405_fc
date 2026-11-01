// Extrai o texto de um PDF com PDFKit (nao ha pdftotext neste Mac).
// Uso: swift tools/pdf_text.swift ARQUIVO.pdf SAIDA.txt
// Cada pagina comeca com uma linha "=====PAGE n=====". PDF so de imagem sai vazio.
import PDFKit
import Foundation

let args = CommandLine.arguments
guard args.count == 3, let doc = PDFDocument(url: URL(fileURLWithPath: args[1])) else {
    print("uso: swift pdf_text.swift ARQUIVO.pdf SAIDA.txt")
    exit(1)
}
var out = ""
for i in 0..<doc.pageCount {
    out += "\n=====PAGE \(i + 1)=====\n" + (doc.page(at: i)?.string ?? "")
}
try! out.write(toFile: args[2], atomically: true, encoding: .utf8)
print("\(doc.pageCount) paginas")
