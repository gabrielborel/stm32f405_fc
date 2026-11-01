// Renderiza uma pagina de PDF em PNG (dobro da resolucao) para ler figuras e desenhos.
// Uso: swift tools/pdf_png.swift ARQUIVO.pdf PAGINA SAIDA.png   (PAGINA comeca em 1)
import PDFKit
import AppKit

let args = CommandLine.arguments
guard args.count == 4,
      let doc = PDFDocument(url: URL(fileURLWithPath: args[1])),
      let n = Int(args[2]), n >= 1, n <= doc.pageCount,
      let page = doc.page(at: n - 1) else {
    print("uso: swift pdf_png.swift ARQUIVO.pdf PAGINA SAIDA.png")
    exit(1)
}
let r = page.bounds(for: .mediaBox)
let s: CGFloat = 2.0
let img = NSImage(size: NSSize(width: r.width * s, height: r.height * s))
img.lockFocus()
NSColor.white.set()
NSRect(x: 0, y: 0, width: r.width * s, height: r.height * s).fill()
let ctx = NSGraphicsContext.current!.cgContext
ctx.scaleBy(x: s, y: s)
page.draw(with: .mediaBox, to: ctx)
img.unlockFocus()
let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: args[3]))
print("ok")
