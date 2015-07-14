class AddVariantesToExamen < ActiveRecord::Migration
  def change
  	remove_column :examen, :variantes
  	add_column :examen, :variantes, :integer, :default => 1
  end
end
