use std::collections::BTreeMap;

#[derive(Debug, Clone)]
pub struct Document {
    title: String,
    tags: Vec<String>,
}

// Borrow titles instead of cloning each document.
pub fn group_titles(documents: &[Document]) -> BTreeMap<&str, Vec<&str>> {
    let mut groups = BTreeMap::new();
    for document in documents {
        for tag in &document.tags {
            groups.entry(tag.as_str())
                .or_insert_with(Vec::new)
                .push(document.title.as_str());
        }
    }
    groups
}

const MAX_DOCUMENTS: usize = 256;
