interface CategoryFilterProps {
  categories: string[];
  selectedCategory: string | null;
  onSelectCategory: (category: string | null) => void;
}

export default function CategoryFilter({
  categories,
  selectedCategory,
  onSelectCategory,
}: CategoryFilterProps) {
  return (
    <div className="flex flex-wrap gap-2 mb-6">
      <button
        className={`px-3 py-1 text-sm rounded-full transition-colors ${
          selectedCategory === null
            ? "bg-gray-800 text-white"
            : "bg-gray-100 text-gray-600 hover:bg-gray-200"
        }`}
        onClick={() => onSelectCategory(null)}
      >
        All
      </button>

      {categories.map((category) => (
        <button
          key={category}
          className={`px-3 py-1 text-sm rounded-full transition-colors ${
            selectedCategory === category
              ? "bg-gray-800 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
          onClick={() => onSelectCategory(category)}
        >
          {category}
        </button>
      ))}
    </div>
  );
}
