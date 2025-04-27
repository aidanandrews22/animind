import { useState, useEffect } from "react";
import IconButton from "./IconButton";
import { PlusIcon, EditIcon } from "./Icons";

interface CourseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (course: {
    title: string;
    description: string;
    category: string;
  }) => void;
  course?: {
    id: string;
    title: string;
    description?: string;
    category?: string;
  };
  mode: 'create' | 'edit';
}

export default function CourseModal({
  isOpen,
  onClose,
  onSave,
  course,
  mode
}: CourseModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");

  // Initialize form with course data when editing
  useEffect(() => {
    if (course && mode === 'edit') {
      setTitle(course.title || "");
      setDescription(course.description || "");
      setCategory(course.category || "");
    }
  }, [course, mode]);

  // Reset form when modal is closed
  useEffect(() => {
    if (!isOpen) {
      setTitle("");
      setDescription("");
      setCategory("");
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    onSave({ title, description, category });
    onClose();
  };

  const modalTitle = mode === 'create' ? 'Create New Course' : 'Edit Course';
  const actionLabel = mode === 'create' ? 'Create Course' : 'Save Changes';
  const actionIcon = mode === 'create' ? <PlusIcon size={16} /> : <EditIcon size={16} />;

  return (
    <div className="fixed inset-0 bg-black/50 bg-opacity-30 flex items-center justify-center z-50">
      <div
        className="bg-surface border border-adaptive rounded-lg p-6 max-w-md w-full shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-medium text-adaptive">
            {modalTitle}
          </h2>
          <span className="text-gray-400 cursor-pointer" onClick={onClose}>
            ✕
          </span>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm text-adaptive opacity-80 mb-1">
              Course Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full p-2 border border-adaptive rounded bg-background text-adaptive"
              placeholder="Enter course title"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm text-adaptive opacity-80 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-2 border border-adaptive rounded bg-background text-adaptive min-h-[100px]"
              placeholder="Enter course description"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm text-adaptive opacity-80 mb-1">
              Category
            </label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full p-2 border border-adaptive rounded bg-background text-adaptive"
              placeholder="Enter category"
            />
          </div>

          <div className="flex justify-end gap-3">
            <IconButton
              type="button"
              label="Cancel"
              icon={<span>✕</span>}
              variant="ghost"
              onClick={onClose}
            />
            <IconButton
              type="submit"
              label={actionLabel}
              icon={actionIcon}
              variant="primary"
            />
          </div>
        </form>
      </div>
    </div>
  );
} 