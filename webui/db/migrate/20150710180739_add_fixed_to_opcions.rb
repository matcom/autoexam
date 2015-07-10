class AddFixedToOpcions < ActiveRecord::Migration
  def change
    add_column :opcions, :fixed, :boolean
  end
end
