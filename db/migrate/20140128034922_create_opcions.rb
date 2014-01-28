class CreateOpcions < ActiveRecord::Migration
  def change
    create_table :opcions do |t|
      t.integer :preguntum_id
      t.text :titulo
      t.boolean :right

      t.timestamps
    end
  end
end
