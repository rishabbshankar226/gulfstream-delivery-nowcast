// Render every page of a PDF to PNG at 2x: swift tools/pdfpages.swift <in.pdf> <out-dir>
import Foundation
import Quartz
let args = CommandLine.arguments
guard args.count == 3, let doc = CGPDFDocument(URL(fileURLWithPath: args[1]) as CFURL) else {
    fputs("usage: pdfpages.swift <in.pdf> <out-dir>\n", stderr); exit(1)
}
let out = URL(fileURLWithPath: args[2])
try? FileManager.default.createDirectory(at: out, withIntermediateDirectories: true)
let scale: CGFloat = 1.5
print("pages \(doc.numberOfPages)")
for i in 1...doc.numberOfPages {
    guard let page = doc.page(at: i) else { continue }
    let box = page.getBoxRect(.mediaBox)
    let w = Int(box.width * scale), h = Int(box.height * scale)
    let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
                        space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1)); ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale); ctx.drawPDFPage(page)
    let url = out.appendingPathComponent(String(format: "page-%02d.png", i))
    let dest = CGImageDestinationCreateWithURL(url as CFURL, "public.png" as CFString, 1, nil)!
    CGImageDestinationAddImage(dest, ctx.makeImage()!, nil); CGImageDestinationFinalize(dest)
}
