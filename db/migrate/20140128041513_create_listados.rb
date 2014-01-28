class CreateListados < ActiveRecord::Migration
  def change
    create_table :listados do |t|
      t.integer :asignatura_id
      t.text :estudiantes

      t.timestamps
    end
  end
end
