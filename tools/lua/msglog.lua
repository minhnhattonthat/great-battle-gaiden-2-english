-- Log every message the text engine starts ($01:85BD, id in $043E) and screenshot each {key} wait ($01:871A)
-- and each message end ($01:86C2): "msg 0A3 f1234", shots m0A3_p1.png, m0A3_end.png. Docs: docs/re/text.md.
local m = emu.memType.snesMemory
local cur, page = nil, 0
local function id() return (emu.read(0x043E, m) | emu.read(0x043F, m) << 8) & 0x0FFF end
L.on_exec(0x0185BD, 0x0185BD, function()
  cur, page = string.format("%03X", id()), 0
  L.log(string.format("msg %s f%d", cur, L.frame))
end)
L.on_exec(0x01871A, 0x01871A, function()
  page = page + 1
  if cur then L.shot(string.format("m%s_p%d.png", cur, page)) end
end)
L.on_exec(0x0186C2, 0x0186C2, function()
  if cur then L.shot(string.format("m%s_end.png", cur)) end
  L.log(string.format("end %s f%d", cur or "?", L.frame))
end)
