class AddMultipleToPregunta < ActiveRecord::Migration
  def change
    add_column :pregunta, :multiple, :boolean, :default => true
  end
end
