local Library = {}
Library.__index = Library

-- Keep entries in insertion order; names are unique.
function Library.new(root)
  return setmetatable({ root = root, entries = {} }, Library)
end

function Library:add(name, metadata)
  assert(type(name) == "string", "expected a document name")
  if self:find(name) then
    return nil, "document already exists"
  end
  self.entries[#self.entries + 1] = {
    name = name,
    title = metadata.title or name,
    tags = metadata.tags or {},
  }
  return true
end

function Library:find(name)
  for index, entry in ipairs(self.entries) do
    if entry.name == name then
      return entry, index
    end
  end
  return nil
end

return Library
